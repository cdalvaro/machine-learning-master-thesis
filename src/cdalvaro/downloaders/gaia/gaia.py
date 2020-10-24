import astropy
from astropy.table import QTable, Table
import astropy.units as u
from astroquery import gaia
import hashlib
import json
import logging
import numpy as np
import os
from typing import List, Set, TypeVar, Union

from ..gaia.metadata import GaiaMetadata
from ...data_base import DB
from ...logging import Logger
from ...models.open_cluster import OpenCluster
from ...models.region import Region

Regions = TypeVar('Regions', bound=Set[Region])
SourceID = TypeVar('SourceID', bound=np.int64)

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
    partition_size: np.int32 = 500_000

    def __init__(self, db: DB, username: str = None, password: str = None, remove_jobs: bool = True):
        self.db = db
        self.username = username
        self.password = password
        self.remove_jobs = remove_jobs
        self._logged = False

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
        self._login()

        number_of_regions = len(regions)
        for counter, region in zip(range(1, number_of_regions + 1), regions):
            try:
                Gaia._logger.info(f"({counter} / {number_of_regions}) Downloading {region} stars from Gaia DR2 ...")
                source_ids = self.db.get_stars_source_id(regions={region})
                self._download_and_save(region=region, extra_size=extra_size, exclude=source_ids)
            except Exception as error:
                Gaia._logger.error(
                    f"An error occurred while downloading stars for region {region} from Gaia DR2 database. Cause: {error}"
                )

        self._logout()
        Gaia._logger.info(f"🏁 Finished downloading stars")

    def _download_and_save(self, region: Region, extra_size: float, exclude: Set[SourceID] = {}):
        """
        Download and save stars for the given region.

        This operation is partitioned to improve memory management.
        Set `Gaia.partition_size` to change the partition size.

        Args:
            region (Region): The region that contains the stars to be downloaded.
            extra_size (float): A positive number with the extra size to extend the region.
            exclude (Set[SourceID]): Source ids to be excluded from the download. Defaults to {}.
        """
        downloaded_ids = exclude.copy()
        while True:
            stars = self._download_partition(region, extra_size=extra_size, exclude=downloaded_ids)
            if stars is not None and len(stars) > 0:
                Gaia._logger.debug(f"Downloaded {len(stars)} stars from Gaia DR2 for region '{region}'")
                downloaded_ids |= set(stars['source_id'])
                self._save_stars(region=region, stars=stars)
                if Gaia.partition_size is None or len(stars) < Gaia.partition_size:
                    Gaia._logger.info(
                        f"Downloaded {len(downloaded_ids) - len(exclude)} new stars for region '{region}'")
                    break
            else:
                if len(exclude) > 0:
                    Gaia._logger.info(f"No new data has been downloaded from Gaia DR2 for region '{region}'")
                else:
                    Gaia._logger.warn(f"No data has been found in the Gaia DR2 database for region '{region}'")
                break

    def _download_partition(self, region: Region, extra_size: float, exclude: Set[SourceID] = {}) -> Table:
        """
        Download data from Gaia DR2 for the given region with an optional extra size
        to extend the given region.

        Args:
            region (Region): The region that contains the stars to be downloaded.
            extra_size (float): A positive number with the extra size to extend the region.
            exclude (Set[SourceID]): Source ids to be excluded from the download. Defaults to {}.

        Returns:
            Table: An astropy table with the downloaded data, or None if an error occurs.
        """
        job = None
        try:
            query, temp_table_name, temp_table = self._compose_query(region=region,
                                                                     extra_size=extra_size,
                                                                     exclude=exclude)
            job = gaia.Gaia.launch_job_async(query, upload_resource=temp_table, upload_table_name=temp_table_name)
            result = job.get_results()
        except Exception as error:
            Gaia._logger.error(f"Error executing job for region {region}. Cause: {error}")
            raise error
        finally:
            if job is not None and self._logged and self.remove_jobs:
                try:
                    gaia.Gaia.remove_jobs(jobs_list=[job.jobid])
                    Gaia._logger.debug(f"Job {job.jobid} successfully removed")
                except Exception as error:
                    Gaia._logger.error(f"Error removing job: {job.jobid} from Gaia server. Cause: {error}")

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

        query = "SELECT" if Gaia.partition_size is None else f"SELECT TOP {Gaia.partition_size}"
        query += f"""
            {', '.join(map(lambda x: f"A.{x}", GaiaMetadata.columns()))}
            FROM {gaia.Gaia.MAIN_GAIA_TABLE} A
            """

        temp_table_name, temp_table = None, None
        if len(exclude) > 0:
            region_md5 = hashlib.md5(region.name.encode('utf-8')).hexdigest()
            temp_table_name = f"cdalvaro_{region_md5}"
            temp_table = Table([list(exclude)],
                               names=['source_id'],
                               dtype=[np.int64],
                               meta={'meta': f"temporary table for region {region}"})

            query += f"""
                LEFT JOIN tap_upload.{temp_table_name} B
                        ON A.source_id = B.source_id
                        WHERE B.source_id IS NULL
                AND
                """
        else:
            query += """
                WHERE
                """

        if hasattr(region, 'diam'):
            radius = region.diam.to_value(u.degree) * extra_size / 2.0
            query += f"""
                1 = CONTAINS(
                    POINT('ICRS', A.ra, A.dec),
                    CIRCLE('ICRS', {ra}, {dec}, {radius})
                )
                """
        else:
            width = region.width.to_value(u.degree) * extra_size
            height = region.height.to_value(u.degree) * extra_size
            query += f"""
                1 = CONTAINS(
                    POINT('ICRS', A.ra, A.dec),
                    BOX('ICRS',
                        {ra}, {dec},
                        {width}, {height})
                )
                """

        query += """
            ORDER BY A.source_id ASC
            """

        return query, temp_table_name, temp_table

    def _save_stars(self, region: Region, stars: Table):
        """
        Method for saving data into cdalvaro database.

        Args:
            region (Region): The region associated with to the data.
            stars (Table): An astropy table with the data to be saved.
        """
        Gaia._logger.debug(f"Saving stars into db ...")

        try:
            stars['priam_flags'] = stars['priam_flags'].astype(np.float64)
            stars['flame_flags'] = stars['flame_flags'].astype(np.float64)
            stars = stars.to_pandas()
            self.db.save_regions([region])
            self.db.save_stars(region=region, stars=stars, columns=stars.columns)
        except Exception as error:
            Gaia._logger.error(f"Error saving data for region {region}. Cause: {error}")

    def _login(self):
        """
        Login to Gaia DR2 database
        """
        if self.username is None or self.password is None:
            self._logged = False
            return

        try:
            Gaia._logger.info("Logging in to Gaia DR2 database...")
            gaia.Gaia.login(user=self.username, password=self.password, verbose=Gaia._logger.level <= logging.DEBUG)
            self._logged = True
        except Exception as error:
            Gaia._logger.error(f"Unable to login to Gaia DR2 database. Cause: {error}")
            self._logged = False

    def _logout(self):
        """
        Logout from Gaia DR2 database
        """
        if self._logged:
            try:
                gaia.Gaia.logout()
            except Exception as error:
                Gaia._logger.error(f"An error occurred while logging out from Gaia DR2. Cause: {error}")
