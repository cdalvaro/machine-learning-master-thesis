import astropy.units as u
from astropy.coordinates import SkyCoord
import os
import pandas
from typing import Set, TypeVar, Union

from ..base_catalogue import BaseCatalogue
from ...logging import Logger
from ...models import OpenCluster

Catalogue = TypeVar('Catalogue', bound=Set[OpenCluster])


class OpenClust(BaseCatalogue):
    """
    Class that contains the OpenClust catalogue.

    More info at: https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html
    """

    _catalogue_file = os.path.join(os.path.dirname(__file__), "clusters.dat")
    _catalogue = dict()
    _logger = Logger.instance()

    @staticmethod
    def catalogue(as_dataframe: bool = False) -> Union[Catalogue, pandas.DataFrame]:
        """
        This method returns the whole OPENCLUST catalogue

        Args:
            as_dataframe (bool, optional): Flag to recover the catalogue as a DataFrame. Defaults to False.

        Returns:
            Union[Catalogue, pandas.DataFrame]: The OPENCLUST catalogue.
        """
        catalogue = OpenClust._load_catalogue()
        if as_dataframe:
            return OpenClust._catalogue_to_dataframe(catalogue)
        return catalogue

    @staticmethod
    def get_clusters(names: Set[str], as_dataframe: bool = False) -> Union[Catalogue, pandas.DataFrame]:
        """
        Get clusters from the catalogue that matches the given names.

        Args:
            names (Set[str]): The name of the clusters to be recovered.

        Returns:
            Catalogue: A catalogue with the found clusters.
        """
        selection = dict()
        whole_catalogue = OpenClust._load_catalogue()
        for name in names:
            if name in whole_catalogue.keys():
                selection[name] = whole_catalogue[name]

        if as_dataframe:
            return OpenClust._catalogue_to_dataframe(selection)

        return selection

    @staticmethod
    def _load_catalogue() -> Catalogue:
        """
        Load the OpenClust catalogue.

        Returns:
            Catalogue: The whole OpenClust catalogue.
        """
        if len(OpenClust._catalogue.keys()) > 0:
            return OpenClust._catalogue

        OpenClust._logger.debug("Loading OpenClust catalogue ...")

        with open(OpenClust._catalogue_file, 'r') as f:
            for line in f.readlines():
                try:
                    cluster = OpenClust._parse_catalogue_entry(line.rstrip())
                    OpenClust._catalogue[cluster.name] = cluster
                except ValueError as ex:
                    OpenClust._logger.warn(ex)

        OpenClust._logger.debug("OpenClust catalogue loaded!")

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
        dec_deg = entry[27:30]
        dec_arcmin = entry[31:33]
        dec_arcsec = entry[34:36]
        dec = f"{dec_deg}:{dec_arcmin}:{dec_arcsec}"
        if len(dec) != 9:
            raise ValueError(f"Cluster {name} does not have a valid declination: '{dec}'")

        coords = SkyCoord(f"{ra} {dec}", unit=(u.hourangle, u.degree), frame="icrs")

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

    @staticmethod
    def _catalogue_to_dataframe(catalogue: Catalogue) -> pandas.DataFrame:
        """
        Method to convert a Catalogue into a Pandas DataFrame.

        Args:
            catalogue (Catalogue): The catalogue to be converted.

        Returns:
            pandas.DataFrame: The catalogue as a DataFrame.
        """
        data = dict()
        for cluster in catalogue.values():
            data[cluster.name] = dict(cluster)
        return pandas.DataFrame.from_dict(data, orient='index')
