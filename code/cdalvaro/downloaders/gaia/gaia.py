from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery import gaia
import json
import logging
import os
import psycopg2
from typing import List, Set, TypeVar

from ..gaia.columns import GaiaColumns
from ...catalogues import OpenClust
from ...data_base import DB
from ...logging import Logger
from ...models.open_cluster import OpenCluster
from ...models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SourceID', bound=str)

# https://astroquery.readthedocs.io/en/latest/api/astroquery.gaia.Conf.html#astroquery.gaia.Conf
GaiaRelease = 'DR2'
gaia.Gaia.MAIN_GAIA_TABLE = 'gaiadr2.gaia_source'
gaia.Gaia.ROW_LIMIT = -1


class Gaia:

    _logger = Logger.instance()
    _columns = GaiaColumns()

    def __init__(self, db: DB):
        self.db = db

    def download(self, regions: Regions, extra_size: float = 1.1):
        for region in regions:
            source_ids = self.db.get_stars(regions={region}, columns=['source_id'])
            source_ids = set(map(lambda x: next(iter(x)), source_ids))
            stars = self._download_stars(region=region, extra_size=extra_size, exclude=source_ids)
            self._save_stars(region=region, stars=stars)

        Gaia._logger.info(f"🏁 Finished downloading stars ...")

    def _download_stars(self, region: Region, extra_size: float, exclude: Set[SourceID]):
        # https://astroquery.readthedocs.io/en/latest/api/astroquery.gaia.GaiaClass.html#astroquery.gaia.GaiaClass

        if hasattr(region, 'diam'):
            query = self._compose_cone_query(region=region, extra_size=extra_size, exclude=exclude)
        else:
            query = self._compose_object_query(region=region, extra_size=extra_size, exclude=exclude)

        result = []
        try:
            Gaia._logger.info(f"⏱ Downloading {region} stars from Gaia {GaiaRelease} ...")
            job = gaia.Gaia.launch_job_async(query, verbose=Gaia._logger.level == logging.DEBUG)
            result = job.get_results()
        except:
            Gaia._logger.error(f"Error executing job")

        Gaia._logger.info(f"Downloaded {len(result)} stars for {region}!")

        return result

    def _compose_cone_query(self, region: Region, extra_size: float, exclude: Set[SourceID]) -> str:
        ra = region.coords.ra.degree
        dec = region.coords.dec.degree
        diam = region.diam.to_value(u.degree) * extra_size

        query = f"""
            SELECT {', '.join(Gaia._columns)}
            FROM {gaia.Gaia.MAIN_GAIA_TABLE}
            WHERE 1 = CONTAINS(
                POINT('ICRS', ra, dec),
                CIRCLE('ICRS', {ra}, {dec}, {diam / 2.0})
            )
            """

        if len(exclude) > 0:
            exclude = list(map(lambda x: str(x), exclude))
            query += f"""
                AND source_id NOT IN ({','.join(exclude)})
                """

        query += """
            ORDER BY source_id ASC
            """

        return query

    def _compose_object_query(self, region: Region, extra_size: float, exclude: Set[SourceID]) -> str:
        raise NotImplementedError

    def _save_stars(self, region: Region, stars: List):
        Gaia._logger.debug(f"💽 Saving recovered stars into db ...")

        # Save cluster
        if isinstance(region, OpenCluster):
            self.db.save_open_clusters([region])

        # Save stars
        self.db.save_stars(region=region, stars=stars, columns=Gaia._columns)
