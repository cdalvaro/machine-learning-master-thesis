import astropy.units as u
import json
import numpy as np
import os
from pandas import DataFrame, read_sql_query
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import execute_values
from psycopg2.extras import LoggingConnection, LoggingCursor
from typing import Dict, List, Set, TypeVar, Union

from .logging import Logger
from .models.open_cluster import OpenCluster
from .models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SolutionID', bound=int)


class DB:

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
    def instance(host: str, port: int):
        key = f"{host}:{port}"
        if key not in DB._instance:
            DB._instance[key] = DB(host=host, port=port)

        return DB._instance[key]

    def get_regions_id(self, regions: Regions, update_regions: bool = True) -> Dict[str, int]:
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Getting regions id for regions: {', '.join(regions_name)} from dab ...")

        query = f"""
            SELECT name, id FROM public.regions
            WHERE name = ANY(%s)
            ORDER BY name ASC
            """

        cursor = self.conn.cursor(cursor_factory=LoggingCursor)
        cursor.execute(query, (regions_name, ))
        result = cursor.fetchall()
        cursor.close()

        regions_id = dict()
        for (name, serial) in result:
            regions_id[name] = serial
            if update_regions and name in regions:
                elements = filter(lambda x: x.name == name, regions)
                element = next(iter(elements))
                element.serial = serial

        return regions_id

    def get_stars_source_id(self, regions: Regions) -> List[str]:
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Getting stars source_id for regions: {', '.join(regions_name)} from db ...")

        query = f"""
            SELECT source_id FROM public.gaiadr2_source
            WHERE region_id = ANY(SELECT id FROM public.regions WHERE name = ANY(%s))
            ORDER BY region_id, source_id ASC
            """

        cursor = self.conn.cursor(cursor_factory=LoggingCursor)
        cursor.execute(query, (regions_name, ))
        result = cursor.fetchall()
        cursor.close()

        return set(map(lambda x: next(iter(x)), result))

    def get_stars(self,
                  region: Region = None,
                  columns: List[str] = None,
                  limit: int = None,
                  use_region_id: bool = True) -> Union[DataFrame, None]:
        DB._logger.debug(f"Getting stars for region {region}")

        if columns is not None:
            required_columns = ['region_id', 'source_id']
            columns = required_columns + list(filter(lambda x: x not in required_columns, columns))
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
            if hasattr(region, 'diam'):
                params.update({
                    'ra': region.coords.ra.degree,
                    'dec': region.coords.dec.degree,
                    'radius': region.diam.value / 2.0
                })

                query += """
                    CIRCLE '((%(ra)s, %(dec)s), %(radius)s)' @> POINT (ra, dec)
                    """
            else:
                # https://www.postgresql.org/docs/current/functions-geometry.html
                # TODO: Implement search by box region
                raise NotImplementedError

        query += """
            ORDER BY region_id, source_id ASC
            """

        if limit is not None:
            params['limit'] = limit
            query += """
                LIMIT %(limit)s
                """

        try:
            return read_sql_query(query, self.conn, index_col=['region_id', 'source_id'], params=params)
        except Exception as error:
            DB._logger.error(f"Error retrieving data for region: {region}. Cause: {error}")
            return None

    def save_open_clusters(self, clusters: List[OpenCluster]):
        clusters_name = list(map(lambda x: x.name, clusters))
        DB._logger.debug(f"Saving clusters: {', '. join(clusters_name)} into db ...")

        query = """
            INSERT INTO public.regions (name, ra, dec, diam, properties)
            VALUES %s ON CONFLICT (name) DO
            UPDATE SET properties = EXCLUDED.properties
            RETURNING id
            """

        data = []
        for cluster in clusters:
            name = cluster.name
            ra = cluster.coords.ra.degree
            dec = cluster.coords.dec.degree
            diam = cluster.diam.value
            properties = {'g1_class': cluster.g1_class}

            data.append((name, ra, dec, diam, json.dumps(properties)))

        cursor = self.conn.cursor(cursor_factory=LoggingCursor)
        serials = execute_values(cursor, query, data, fetch=True)
        self.conn.commit()
        cursor.close()

        for cluster, serial in zip(clusters, serials):
            cluster.serial = next(iter(serial))

    def save_stars(self, region: Region, stars: List, columns: List[str]):
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

        cursor = self.conn.cursor(cursor_factory=LoggingCursor)
        execute_values(cursor, query, data, page_size=10000)
        self.conn.commit()
        cursor.close()
