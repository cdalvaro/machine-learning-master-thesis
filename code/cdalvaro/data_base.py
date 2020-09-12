import astropy.units as u
import json
import numpy as np
import os
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import execute_values
from psycopg2.extras import LoggingConnection, LoggingCursor
from typing import List, Set, TypeVar

from .logging import Logger
from .models.open_cluster import OpenCluster
from .models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SolutionID', bound=int)


class DB:

    _logger: Logger = Logger.instance()
    _instance = dict()

    psycopg2.extensions.register_adapter(np.bool_, psycopg2._psycopg.AsIs)
    psycopg2.extensions.register_adapter(np.int16, psycopg2._psycopg.AsIs)
    psycopg2.extensions.register_adapter(np.int32, psycopg2._psycopg.AsIs)
    psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
    psycopg2.extensions.register_adapter(np.float32, psycopg2._psycopg.AsIs)
    psycopg2.extensions.register_adapter(np.float64, psycopg2._psycopg.AsIs)

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

    def get_stars(self, regions: Regions, columns: List[str] = None) -> List:
        regions_name = list(map(lambda x: x.name, regions))
        DB._logger.debug(f"Getting stars for regions: {','.join(regions_name)} from db ...")

        if not columns or len(columns) == 0:
            columns = ['*']

        query = f"""
            SELECT {', '.join(columns)} FROM public.gaiadr2_source
            WHERE region_id = ANY(SELECT id FROM public.regions WHERE name = ANY(%s))
            ORDER BY region_id, source_id ASC
            """

        cursor = self.conn.cursor(cursor_factory=LoggingCursor)
        cursor.execute(query, (regions_name, ))
        result = cursor.fetchall()
        cursor.close()

        return result

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

    def save_stars(self, region: Region, stars: List, columns: List):
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
