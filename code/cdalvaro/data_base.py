from __future__ import annotations

import astropy
from astropy.coordinates import SkyCoord
import astropy.units as u
import json
import numpy as np
import os
import pandas
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import execute_values
from psycopg2.extras import LoggingConnection, LoggingCursor
from typing import Dict, List, Set, TypeVar, Union

from .catalogues.base_catalogue import Catalogue
from .logging import Logger
from .models.open_cluster import OpenCluster
from .models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SolutionID', bound=int)


class DB:
    """
    cdalvaro data base class to manage actions over the database.

    Args:
        host (str): The database hostname.
        port (int): The port where the database is listening.
    """

    _logger: Logger = Logger.instance()
    _instance = dict()

    register_adapter(np.bool_, AsIs)
    register_adapter(np.int16, AsIs)
    register_adapter(np.int32, AsIs)
    register_adapter(np.int64, AsIs)
    register_adapter(np.float32, AsIs)
    register_adapter(np.float64, AsIs)

    def __init__(self, host: str, port: int):
        db_settings = {
            'dbname': os.getenv('POSTGRES_DB', 'gaia'),
            'user': os.getenv('POSTGRES_USER', 'gaia'),
            'password': os.getenv('POSTGRES_PASSWORD', 'gaia'),
            'host': host,
            'port': port
        }

        self.conn = psycopg2.connect(connection_factory=LoggingConnection, **db_settings)
        self.conn.initialize(DB._logger)

    def __del__(self):
        self.conn.close()

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

        query = f"""
            SELECT name, id FROM public.regions
            WHERE name = ANY(%s)
            ORDER BY name ASC
            """

        try:
            cursor = self.conn.cursor(cursor_factory=LoggingCursor)
            cursor.execute(query, (regions_name, ))
            result = cursor.fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering regions id from DB. Cause: {error}")
            raise error
        finally:
            cursor.close()

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

        query = f"""
            SELECT source_id FROM public.gaiadr2_source
            WHERE region_id = ANY(SELECT id FROM public.regions WHERE name = ANY(%s))
            ORDER BY region_id, source_id ASC
            """

        try:
            cursor = self.conn.cursor(cursor_factory=LoggingCursor)
            cursor.execute(query, (regions_name, ))
            result = cursor.fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering stars source_id from DB. Cause: {error}")
            raise error
        finally:
            cursor.close()

        return set(map(lambda x: next(iter(x)), result))

    def get_regions(self, names: Set[str] = {}, as_dataframe: bool = False) -> Union[Catalogue, pandas.DataFrame]:
        """
        Get the regions matching the given names.

        Args:
            names (Set[str]): A set with the names with the regions to retrieve.
            as_dataframe (bool, optional): Flag to recover regions as a DataFrame. Defaults to False.

        Returns:
            Union[Catalogue, pandas.DataFrame]: A catalogue with found regions.
        """
        columns = ('name', 'ra', 'dec', 'diam', 'width', 'height')
        query = f"SELECT {', '. join(columns)} FROM public.regions"

        if len(names) > 0:
            DB._logger.debug(f"Getting regions: {names} from DB ...")
            query += " WHERE name = ANY(%s)"
            params = (list(names), )
        else:
            DB._logger.debug(f"Getting all regions from DB ...")
            params = ()

        if as_dataframe:
            index_col = 'name'
            try:
                return pandas.read_sql_query(query, self.conn, index_col=index_col, params=params)
            except Exception as error:
                DB._logger.error(f"An error ocurred recovering regions dataframe from DB. Cause: {error}")
                raise error

        try:
            cursor = self.conn.cursor(cursor_factory=LoggingCursor)
            cursor.execute(query, params)
            result = cursor.fetchall()
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering regions catalogue from DB. Cause: {error}")
            raise error
        finally:
            cursor.close()

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
                  region: Region = None,
                  columns: List[str] = None,
                  limit: int = None,
                  use_region_id: bool = True,
                  extra_size: float = 1.0) -> pandas.DataFrame:
        """
        Returns a Pandas DataFrame containing the stars of the given region.

        Args:
            region (Region): The region which contains the stars.
            columns (List[str], optional): A list with the data fields to be recovered. Defaults all columns.
            limit (int, optional): The maximum number of stars to be recovered. Defaults no limit.
            use_region_id (bool, optional): Use the region_id to get stars. If False select starts by position fields. Defaults to True.
            extra_size (float, optional): A positive number to extend the region which contains the stars to be recovered. Defaults to 1.0.

        Returns:
            DataFrame: A Pandas DataFrame with the recovered stars
        """
        DB._logger.debug(f"Getting stars for region {region}")

        index_columns = ['region_id', 'source_id']
        if columns is not None:
            columns = index_columns + list(filter(lambda x: x not in index_columns, columns))
        else:
            columns = ['*']

        query = f"""
            SELECT {', '.join(columns)} FROM public.gaiadr2_source
            WHERE
            """

        params = dict()
        if use_region_id:
            params['name'] = region.name
            query += """
                region_id = (SELECT id FROM public.regions WHERE name = %(name)s)
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

        query += """
            ORDER BY region_id, source_id ASC
            """

        if limit is not None:
            params['limit'] = limit
            query += """
                LIMIT %(limit)s
                """

        try:
            return pandas.read_sql_query(query, self.conn, index_col=index_columns, params=params)
        except Exception as error:
            DB._logger.error(f"An error ocurred recovering data for region: {region} from DB. Cause: {error}")
            raise error

    def save_regions(self, regions: Regions):
        """
        Save the given regions into the database.

        Args:
            regions (Regions): The regions to be saved into the database.
        """
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Saving regions: {', '. join(regions_name)} into db ...")

        query = """
            INSERT INTO public.regions (name, ra, dec, diam, properties)
            VALUES %s ON CONFLICT (name) DO
            UPDATE SET properties = EXCLUDED.properties
            RETURNING id
            """

        data = []
        for region in regions:
            name = region.name
            ra = region.coords.ra.degree
            dec = region.coords.dec.degree
            diam = region.diam.value
            if isinstance(region, OpenCluster):
                properties = {'g1_class': region.g1_class}
            else:
                properties = dict()

            data.append((name, ra, dec, diam, json.dumps(properties)))

        try:
            cursor = self.conn.cursor(cursor_factory=LoggingCursor)
            serials = execute_values(cursor, query, data, fetch=True)
            self.conn.commit()
        except Exception as error:
            DB._logger.error(f"An error ocurred saving regions data into DB. Cause: {error}")
            self.conn.rollback()
            raise error
        finally:
            cursor.close()

        for region, serial in zip(regions, serials):
            region.serial = next(iter(serial))

    def save_stars(self, region: Region, stars: astropy.table, columns: List[str]):
        """
        Save the stars associated to the given region into the database.

        Args:
            region (Region): The region containing the stars.
            starts (astropy.table): The table with the stars to be saved into the database.
            columns (List[str]): A list with the columns to be saved into the database.
        """
        DB._logger.debug(f"Saving stars for region {region} into db ...")

        required_columns = ['region_id', 'source_id', 'solution_id', 'designation']
        columns = required_columns + list(filter(lambda x: x not in required_columns, columns))

        query = f"""
            INSERT INTO public.gaiadr2_source ({','.join(columns)})
            VALUES %s ON CONFLICT (region_id, source_id) DO NOTHING
            """

        columns.remove('region_id')

        data = []
        for star in stars:
            try:
                star_data = [region.serial]
                for column in columns:
                    value = star[column]
                    if isinstance(value, np.ma.core.MaskedConstant):
                        try:
                            value = int(f"{value}")
                        except ValueError:
                            value = None
                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    star_data.append(value)
                data.append(star_data)
            except Exception as error:
                self._logger.error(f"Error processing star {star['source_id']}. Cause: {error}")

        if len(data) == 0:
            return

        try:
            cursor = self.conn.cursor(cursor_factory=LoggingCursor)
            execute_values(cursor, query, data, page_size=10000)
            self.conn.commit()
        except Exception as error:
            DB._logger.error(f"An error ocurred saving stars data into DB. Cause: {error}")
            self.conn.rollback()
            raise error
        finally:
            cursor.close()
