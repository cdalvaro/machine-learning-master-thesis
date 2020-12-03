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
        trumpler (str): Trumpler type determined in the DSS inspection
        g1_class (str, optional): Flag for classification of the cluster (G1). Defaults to None.
        number_of_cluster_members (int, optional): Estimated number of cluster members. Defaults to None.
    """
    def __init__(self,
                 name: str,
                 coords: SkyCoord,
                 diam: u.Quantity,
                 trumpler: str,
                 g1_class: str = None,
                 number_of_cluster_members: int = None):
        super().__init__(name=name, coords=coords, diam=diam)
        self.trumpler = trumpler
        self.g1_class = g1_class
        self.number_of_cluster_members = number_of_cluster_members

    def __iter__(self):
        yield 'name', self.name
        yield 'ra', self.coords.ra.degree
        yield 'dec', self.coords.dec.degree
        yield 'diam', self.diam.to_value(u.degree)
        yield 'trumpler', self.trumpler
        yield 'g1_class', self.g1_class
        yield 'number_of_cluster_members', self.number_of_cluster_members
