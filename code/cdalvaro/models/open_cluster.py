from astropy.coordinates import SkyCoord
from astropy.units import Quantity

from .region import Region


class OpenCluster(Region):
    def __init__(self, name: str, coords: SkyCoord, diam: Quantity, g1_class: str = None):
        """
        Class for storing OPENCLUST clusters information

        https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html

        Args:
            name (str): The name of the cluster
            coords (SkyCoord): The coordinates of the cluster
            diam (Quantity): The diameter of the cluster
            g1_class (str, optional): Flag for classification of the cluster (G1). Defaults to None.
        """
        super().__init__(name=name, coords=coords, diam=diam)
        self.g1_class = g1_class
