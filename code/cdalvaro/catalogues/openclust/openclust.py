import os
import logging

from astropy.coordinates import SkyCoord
import astropy.units as u

from ..base_catalogue import BaseCatalogue, Catalogue
from ...info import Cluster


class OpenClust(BaseCatalogue):

    catalogue_file = os.path.join(os.path.dirname(__file__), "clusters.dat")

    @staticmethod
    def load_catalogue() -> Catalogue:
        catalogue = dict()
        with open(OpenClust.catalogue_file, 'r') as f:
            for line in f.readlines():
                try:
                    cluster = OpenClust._parse_catalogue_entry(line.rstrip())
                    catalogue[cluster] = cluster
                except ValueError as ex:
                    logging.error(ex)

        return catalogue

    @staticmethod
    def _parse_catalogue_entry(entry: str) -> Cluster:
        # Fields information is avaiable at ReadMe.txt file

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
            raise ValueError(
                f"Cluster {name} does not have a valid right ascension: '{ra}'")

        # Declination
        de_deg = entry[27:30]
        de_arcmin = entry[31:33]
        de_arcsec = entry[34:36]
        de = f"{de_deg}:{de_arcmin}:{de_arcsec}"
        if len(de) != 9:
            raise ValueError(
                f"Cluster {name} does not have a valid declination: '{de}'")

        coords = SkyCoord(f"{ra} {de}", unit=(
            u.hourangle, u.deg), frame="icrs")

        # G1 class
        g1_class = entry[37:39].strip()
        if len(g1_class) == 0:
            g1_class = None

        # Diameter
        diam = entry[40:47].strip()
        if len(diam) == 0:
            raise ValueError(f"Cluster '{name}' does not have diameter info")
        diam = u.Quantity(diam, u.deg)

        return Cluster(name=name, coords=coords, diameter=diam, g1_class=g1_class)
