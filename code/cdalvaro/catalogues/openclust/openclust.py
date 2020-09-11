import astropy.units as u
from astropy.coordinates import SkyCoord
import os
from typing import Set, TypeVar

from ..base_catalogue import BaseCatalogue
from ...logging import Logger
from ...models import OpenCluster

Catalogue = TypeVar('Catalogue', bound=Set[OpenCluster])


class OpenClust(BaseCatalogue):

    _catalogue_file = os.path.join(os.path.dirname(__file__), "clusters.dat")
    _catalogue = dict()
    _logger = Logger.instance()

    @staticmethod
    def load_catalogue() -> Catalogue:
        """
        Load OpenClust catalogue.

        https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html

        Returns:
            Catalogue: The whole OpenClust catalogue
        """
        if len(OpenClust._catalogue.keys()) > 0:
            return OpenClust._catalogue

        OpenClust._logger.info("Loading OpenClust catalogue ...")

        with open(OpenClust._catalogue_file, 'r') as f:
            for line in f.readlines():
                try:
                    cluster = OpenClust._parse_catalogue_entry(line.rstrip())
                    OpenClust._catalogue[cluster.name] = cluster
                except ValueError as ex:
                    OpenClust._logger.warn(ex)

        OpenClust._logger.info("OpenClust catalogue loaded!")

        return OpenClust._catalogue

    @staticmethod
    def _parse_catalogue_entry(entry: str) -> OpenCluster:
        """
        Method for parsing each entry of the catalogue.

        Information about the content of clusters.dat file
        is available inside ReadMe.txt

        Args:
            entry (str): Each row of the clusters.dat file

        Returns:
            OpenCluster: An OpenCluster object with the cluster information
        """

        # Cluster name
        name = entry[0:17].strip()
        if len(name) == 0:
            raise ValueError("Cluster unable to create a cluster without name")

        # Right Ascension
        ra_hours = entry[18:20]
        ra_minutes = entry[21:23]
        ra_seconds = entry[24:26]
        ra = f"{ra_hours}:{ra_minutes}:{ra_seconds}"
        if len(ra) != 8:
            raise ValueError(f"Cluster {name} does not have a valid right ascension: '{ra}'")

        # Declination
        de_deg = entry[27:30]
        de_arcmin = entry[31:33]
        de_arcsec = entry[34:36]
        de = f"{de_deg}:{de_arcmin}:{de_arcsec}"
        if len(de) != 9:
            raise ValueError(f"Cluster {name} does not have a valid declination: '{de}'")

        coords = SkyCoord(f"{ra} {de}", unit=(u.hourangle, u.deg), frame="icrs")

        # G1 class
        g1_class = entry[37:39].strip()
        if len(g1_class) == 0:
            g1_class = None

        # Diameter
        diam = entry[40:47].strip()
        if len(diam) == 0:
            raise ValueError(f"Cluster '{name}' does not have diameter info")
        diam = u.Quantity(diam, u.arcmin)

        OpenClust._logger.debug(f"Loaded cluster: {name}")

        return OpenCluster(name=name, coords=coords, diam=diam, g1_class=g1_class)
