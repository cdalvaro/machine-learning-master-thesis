from __future__ import annotations

from astropy.coordinates import SkyCoord
import astropy.units as u
import json
import numpy as np
import os
import pandas as pd
from sqlalchemy import create_engine, MetaData, select, any_
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, List, Set, TypeVar, Union

from .catalogues.base_catalogue import Catalogue
from .logging import Logger
from .models.open_cluster import OpenCluster
from .models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SourceID', bound=int)


class DB:
    """
    cdalvaro data base class to manage actions over the database.

    Args:
        host (str): The database hostname.
        port (int): The port where the database is listening.
    """

    _logger: Logger = Logger.instance()
    _instance = dict()

    def __init__(self, host: str, port: int):
        db_settings = {
            'dbname': os.getenv('POSTGRES_DB', 'gaia'),
            'user': os.getenv('POSTGRES_USER', 'gaia'),
            'password': os.getenv('POSTGRES_PASSWORD', 'gaia'),
            'host': host,
            'port': port
        }

        conn_str = "{}://{}:{}@{}:{}/{}".format("postgresql+psycopg2", db_settings["user"], db_settings["password"],
                                                db_settings["host"], db_settings["port"], db_settings["dbname"])

        self.engine = create_engine(conn_str, pool_recycle=3600, execution_options={'autocommit': True})
        self.metadata = MetaData(self.engine)
        self.metadata.reflect()

    @staticmethod
    def instance(host: str, port: int) -> DB:
        """
        Returns a database manager instance pointed to host:port

        Args:
            host (str): The database hostname.
            port (int): The port where the database is listening.

        Returns:
            DB: A cdalvaro DB instance pointing to host:port
        """
        key = f"{host}:{port}"
        if key not in DB._instance:
            DB._instance[key] = DB(host=host, port=port)

        return DB._instance[key]

    def get_regions_id(self, regions: Regions, update_regions: bool = True) -> Dict[str, int]:
        """
        Returns a dictionary where the keys are the regions name,
        and values are the ids of the corresponding region.

        Args:
            regions (Regions): A set with regions whose ids are going to be recovered.
            update_regions (bool, optional): If True, regions set is updated with their corresponding id. Defaults to True.

        Returns:
            Dict[str, int]: A dictionary relating region names with their corresponding ids.
        """
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Getting regions id for regions: {', '.join(regions_name)} from DB ...")

        try:
            regions_t = self.metadata.tables['regions']
            select_stmt = select([regions_t.c.name, regions_t.c.id
                                  ]).where(regions_t.c.name == any_(regions_name)).order_by(regions_t.c.name)

            with self.engine.connect() as connection:
                result = connection.execute(select_stmt).fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering regions id from DB. Cause: {error}")
            raise error

        regions_id = dict()
        for (name, serial) in result:
            regions_id[name] = serial
            if update_regions and name in regions:
                region, *_ = filter(lambda x: x.name == name, regions)
                region.serial = serial

        return regions_id

    def get_stars_source_id(self, regions: Regions) -> List[str]:
        """
        Get a list of source_id's of the stars available in the database
        contained inside the given regions.

        Args:
            regions (Regions): The regions that contains the stars of interest.

        Returns:
            List[str]: A list with the source_id of every star inside the given regions.
        """
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Getting the stars's source_id for regions: {', '.join(regions_name)} from DB ...")

        try:
            gaiadr2_t = self.metadata.tables['gaiadr2_source']

            region_ids = list(self.get_regions_id(regions=regions).values())
            select_stmt = select([gaiadr2_t.c.source_id
                                  ]).select_from(gaiadr2_t).where(gaiadr2_t.c.region_id == any_(region_ids)).order_by(
                                      gaiadr2_t.c.region_id, gaiadr2_t.c.source_id)

            with self.engine.connect() as connection:
                result = connection.execute(select_stmt).fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering stars source_id from DB. Cause: {error}")
            raise error

        return set(map(lambda x: next(iter(x)), result))

    def get_regions(self, names: Set[str] = {}, as_dataframe: bool = False) -> Union[Catalogue, pd.DataFrame]:
        """
        Get the regions matching the given names.

        Args:
            names (Set[str]): A set with the names with the regions to retrieve.
            as_dataframe (bool, optional): Flag to recover regions as a DataFrame. Defaults to False.

        Returns:
            Union[Catalogue, pd.DataFrame]: A catalogue with found regions.
        """
        columns = ('name', 'ra', 'dec', 'diam', 'width', 'height')
        query = f"SELECT {', '. join(columns)} FROM public.regions"

        params = dict()
        if len(names) > 0:
            DB._logger.debug(f"Getting regions: {names} from DB ...")
            query += " WHERE name = ANY(%(regions_name)s)"
            params['regions_name'] = list(names)
        else:
            DB._logger.debug(f"Getting all regions from DB ...")

        if as_dataframe:
            index_col = 'name'
            try:
                return pd.read_sql_query(query, self.engine, index_col=index_col, params=params)
            except Exception as error:
                DB._logger.error(f"An error ocurred recovering regions dataframe from DB. Cause: {error}")
                raise error

        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, params).fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering regions catalogue from DB. Cause: {error}")
            raise error

        catalogue = dict()
        for (name, ra, dec, diam, width, height) in result:
            if name is None:
                continue

            coords = SkyCoord(f"{ra} {dec}", unit=(u.degree, u.degree), frame="icrs")
            properties = dict()
            if diam is not None:
                properties = {'diam': u.Quantity(diam, u.arcmin)}
            else:
                properties = {'width': u.Quantity(width, u.arcmin), 'height': u.Quantity(height, u.arcmin)}

            catalogue[name] = Region(name=name, coords=coords, **properties)

        return catalogue

    def get_stars(self,
                  region: Region,
                  columns: List[str] = None,
                  limit: int = None,
                  use_region_id: bool = True,
                  extra_size: float = 1.0,
                  filter_null_columns: Union[bool, Set[str]] = False) -> pd.DataFrame:
        """
        Returns a Pandas DataFrame containing the stars of the given region.

        Args:
            region (Region): The region which contains the stars.
            columns (List[str], optional): A list with the data fields to be recovered. Defaults all columns.
            limit (int, optional): The maximum number of stars to be recovered. Defaults no limit.
            use_region_id (bool, optional): Use the region_id to get stars. If False select starts by position fields. Defaults to True.
            extra_size (float, optional): A positive number to extend the region which contains the stars to be recovered. Defaults to 1.0.
            filter_null_columns (Union[bool, Set[str]], optional): Filter entries with null values in the given columns. Defaults to False.

        Returns:
            DataFrame: A Pandas DataFrame with the recovered stars
        """
        DB._logger.debug(f"Getting stars for region {region}")

        index_columns = ['region_id', 'source_id']
        if columns is not None and '*' not in columns:
            columns = index_columns + list(filter(lambda x: x not in index_columns, columns))
        else:
            columns = ['*']

        query = f"""
            SELECT {', '.join(columns)} FROM public.gaiadr2_source
            WHERE
            """

        params = dict()
        if use_region_id:
            region_ids = self.get_regions_id(regions=set([region])).values()
            if len(region_ids) == 0:
                raise RuntimeError(f"Region '{region.name}' is not available in DB")
            params['region_id'] = next(iter(region_ids))
            query += """
                region_id = %(region_id)s
                """
        else:
            # https://www.postgresql.org/docs/current/functions-geometry.html
            if hasattr(region, 'diam'):
                params.update({
                    'ra': region.coords.ra.degree,
                    'dec': region.coords.dec.degree,
                    'radius': region.diam.to_value(u.degree) * extra_size / 2.0
                })

                query += """
                    CIRCLE(POINT(%(ra)s, %(dec)s), %(radius)s) @> POINT(ra, dec)
                    """
            else:
                params.update({
                    'ra1': region.coords.ra.degree - region.width.to_value(u.degree) / 2.0,
                    'dec1': region.coords.dec.degree - region.height.to_value(u.degree) / 2.0,
                    'ra2': region.coords.ra.degree + region.width.to_value(u.degree) / 2.0,
                    'dec2': region.coords.dec.degree + region.height.to_value(u.degree) / 2.0
                })

                query += """
                    BOX(POINT(%(ra1)s, %(dec1)s), POINT(%(ra2)s, %(dec2)s)) @> POINT(ra, dec)
                    """

        if isinstance(filter_null_columns, bool):
            if filter_null_columns:
                if '*' in columns:
                    query += "AND gaiadr2_source IS NOT NULL"
                else:
                    columns = list(filter(lambda column: column not in index_columns, columns))
                    query += " ".join(list(map(lambda column: f"AND {column} IS NOT NULL", columns)))
        elif len(filter_null_columns) > 0:
            if '*' in filter_null_columns:
                query += "AND gaiadr2_source IS NOT NULL"
            else:
                filter_null_columns = set(filter(lambda column: column not in index_columns, filter_null_columns))
                query += " ".join(list(map(lambda column: f"AND {column} IS NOT NULL", filter_null_columns)))

        query += """
            ORDER BY region_id, source_id ASC
            """

        if limit is not None:
            params['limit'] = limit
            query += """
                LIMIT %(limit)s
                """

        try:
            return pd.read_sql_query(query, self.engine, index_col=index_columns, params=params)
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering data for region: {region} from DB. Cause: {error}")
            raise error

    def save_regions(self, regions: Regions):
        """
        Save given regions into the database.

        Args:
            regions (Regions): The regions to be saved into the database.
        """
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Saving regions: {', '. join(regions_name)} into db ...")

        data = []
        for region in regions:
            entry = {
                'name': region.name,
                'ra': region.coords.ra.degree,
                'dec': region.coords.dec.degree,
                'diam': region.diam.value,
                'properties': dict()
            }

            if isinstance(region, OpenCluster):
                entry['properties'] = {'g1_class': region.g1_class, 'trumpler': region.trumpler}

            data.append(entry)

        try:
            regions_table = self.metadata.tables['regions']

            # https://docs.sqlalchemy.org/en/13/dialects/postgresql.html
            # https://docs.sqlalchemy.org/en/13/dialects/postgresql.html#sqlalchemy.dialects.postgresql.Insert.on_conflict_do_update
            insert_stmt = insert(regions_table).values(data).returning(regions_table.c.id)
            do_update_stmt = insert_stmt.on_conflict_do_update(index_elements=['name'],
                                                               set_=dict(properties=insert_stmt.excluded.properties))

            with self.engine.connect() as connection:
                serials = connection.execute(do_update_stmt).fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred saving regions data into DB. Cause: {error}")
            raise error

        for region, serial in zip(regions, serials):
            region.serial = next(iter(serial))

    def save_stars(self, region: Region, stars: pd.DataFrame):
        """
        Save the stars associated to the given region into the database.

        Args:
            region (Region): The region containing the stars.
            starts (pd.DataFrame): The DataFrame with the stars to be saved into the database.
        """
        DB._logger.debug(f"Saving stars for region {region} into db ...")

        stars.insert(0, "region_id", np.full(len(stars), fill_value=region.serial, dtype=np.int32))
        stars.set_index(['region_id', 'source_id'], inplace=True)

        try:
            with self.engine.connect() as connection:
                stars.to_sql('gaiadr2_source',
                             con=connection,
                             if_exists='append',
                             index=True,
                             chunksize=100_000,
                             method='multi')
        except Exception as error:
            DB._logger.error(f"An error ocurred saving stars data into DB. Cause: {error}")
            raise error
