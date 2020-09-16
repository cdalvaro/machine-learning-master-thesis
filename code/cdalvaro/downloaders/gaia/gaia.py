import astropy
import astropy.units as u
from astroquery import gaia
import json
import logging
import os
import psycopg2
from typing import List, Set, TypeVar

from ..gaia.columns import GaiaColumns
from ...data_base import DB
from ...logging import Logger
from ...models.open_cluster import OpenCluster
from ...models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SourceID', bound=str)

# https://astroquery.readthedocs.io/en/latest/api/astroquery.gaia.Conf.html#astroquery.gaia.Conf
gaia.Gaia.MAIN_GAIA_TABLE = 'gaiadr2.gaia_source'
gaia.Gaia.ROW_LIMIT = -1


class Gaia:
    """
    Class for downloading data from Gaia DR2 and save into cdalvaro DB

    Args:
        db (DB): A cdalvaro DB object for saving data.
    """

    _logger = Logger.instance()
    _columns = GaiaColumns()

    def __init__(self, db: DB):
        self.db = db

    def download_and_save(self, regions: Regions, extra_size: float = 1.0):
        """
        Download stars information from Gaia DR2 for the given regions
        with an optional extra size to extend the region and save the downloaded
        data into a cdalvaro database.

        Args:
            regions (Regions): Regions that contain the stars to download.
            extra_size (float, optional): A positive number with the extra size to extend the region. Defaults to 1.0.
        """
        if extra_size < 0.0:
            extra_size = abs(extra_size)
            Gaia._logger.warn(f"extra_size parameter must be positive. Absolute value will be taken: {(extra_size)}")

        Gaia._logger.info("⏱ Starting download ...")

        number_of_regions = len(regions)
        for counter, region in zip(range(1, number_of_regions + 1), regions):
            Gaia._logger.info(f"({counter}/{number_of_regions}) Downloading {region} stars from Gaia DR2 ...")
            source_id = self.db.get_stars_source_id(regions={region})
            stars = self._download_stars(region=region, extra_size=extra_size, exclude=source_id)
            if len(stars) > 0:
                self._save_stars(region=region, stars=stars)

        Gaia._logger.info(f"🏁 Finished downloading stars ...")

    def _download_stars(self, region: Region, extra_size: float, exclude: Set[SourceID] = {}) -> astropy.table:
        """
        Download data from Gaia DR2 for the given region with an optional extra size
        to extend the given region.

        Args:
            region (Region): The region that contains the stars to be downloaded.
            extra_size (float): A positive number with the extra size to extend the region.
            exclude (Set[SourceID]): Source ids to be excluded from the download.

        Returns:
            astropy.table: An astropy table with the downloaded data.
        """
        try:
            query = self._compose_query(region=region, extra_size=extra_size, exclude=exclude)
            job = gaia.Gaia.launch_job_async(query, verbose=Gaia._logger.level == logging.DEBUG)
            result = job.get_results()
            Gaia._logger.info(f"Downloaded {len(result)} stars for {region}")
        except Exception as error:
            result = []
            Gaia._logger.error(f"Error executing job for region {region}. Cause: {error}")

        return result

    def _compose_query(self, region: Region, extra_size: float, exclude: Set[SourceID]) -> str:
        """
        Compose the query to download data from Gaia DR2 for the given region.

        astroquery.gaia class info:
        https://astroquery.readthedocs.io/en/latest/api/astroquery.gaia.GaiaClass.html#astroquery.gaia.GaiaClass

        Args:
            region (Region): The region that contains the stars to be downloaded.
            extra_size (float): A positive number to extend the given region diameter.
            exclude (Set[SourceID]): Source ids to be excluded from the download.

        Returns:
            str: A string with the download query.
        """
        ra = region.coords.ra.degree
        dec = region.coords.dec.degree

        query = f"""
            SELECT {', '.join(Gaia._columns)}
            FROM {gaia.Gaia.MAIN_GAIA_TABLE}
            WHERE 1 =
            """

        if hasattr(region, 'diam'):
            radius = region.diam.to_value(u.degree) * extra_size / 2.0
            query += f"""
                CONTAINS(
                    POINT('ICRS', ra, dec),
                    CIRCLE('ICRS', {ra}, {dec}, {radius})
                )
                """
        else:
            width = region.width.to_value(u.degree) * extra_size
            height = region.height.to_value(u.degree) * extra_size
            query += f"""
                CONTAINS(
                    POINT('ICRS', ra, dec),
                    BOX('ICRS',
                        {ra}, {dec},
                        {width}, {height})
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

    def _save_stars(self, region: Region, stars: astropy.table):
        """
        Method for saving data into cdalvaro database.

        Args:
            region (Region): The region associated with to the data.
            stars (astropy.table): An astropy table with the data to be saved.
        """
        Gaia._logger.debug(f"Saving stars into db ...")

        try:
            self.db.save_regions([region])
            self.db.save_stars(region=region, stars=stars, columns=Gaia._columns)
        except Exception as error:
            Gaia._logger.error(f"Error saving data for region {region}. Cause: {error}")
