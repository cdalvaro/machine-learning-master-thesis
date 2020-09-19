from astropy.coordinates import SkyCoord
import astropy.units as u

from .region import Region


class OpenCluster(Region):
    """
    Class for storing OPENCLUST clusters information

    https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html

    Args:
        name (str): The name of the cluster.
        coords (SkyCoord): The coordinates of the cluster.
        diam (astropy.units.Quantity): The diameter of the cluster.
        g1_class (str, optional): Flag for classification of the cluster (G1). Defaults to None.
    """
    def __init__(self, name: str, coords: SkyCoord, diam: u.Quantity, g1_class: str = None):
        super().__init__(name=name, coords=coords, diam=diam)
        self.g1_class = g1_class

    def __iter__(self):
        yield 'name', self.name
        yield 'ra', self.coords.ra.degree
        yield 'dec', self.coords.dec.degree
        yield 'diam', self.diam.to_value(u.degree)
        yield 'g1_class', self.g1_class
