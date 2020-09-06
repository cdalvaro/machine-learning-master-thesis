from astropy.coordinates import SkyCoord
from astropy.units import Quantity


class Cluster:

    def __init__(self, name: str, coords: SkyCoord, diameter: Quantity, g1_class: str = None):
        """
        Basic class for storing cluster information

        Args:
            name (str): The name of the cluster
            coords (SkyCoord): The coordinates of the cluster
            diameter (Quantity): The diameter of the cluster
            g1_class (str, optional): Flag for classification of the cluster (G1). Defaults to None.
        """
        self.name = name
        self.coords = coords
        self.diameter = diameter
        self.g1_class = g1_class

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: 'Cluster') -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
