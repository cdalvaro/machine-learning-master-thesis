from astropy.coordinates import SkyCoord
from astropy.units import Quantity


class Region:
        """
        This is the base class for describing a region.

        You must specify the diameter (diam) or
        the height and width of the region but not both at the same time.

        Args:
            name (str): The name of the region.
            coords (SkyCoord): The coordinates of the region.
            diam (Quantity, optional): The diameter of the region. Defaults to None.
            height (Quantity, optional): The height of the region. Defaults to None.
            width (Quantity, optional): The width of the region. Defaults to None.
            serial (int): The serial id of the region in the cdalvaro database. Defaults to None.

        Raises:
            ValueError: If either diam neither height or width are specified.
            ValueError: If diam and height or width are specified at the same time.
            ValueError: If height and width are not specified at the same time.
        """

    def __init__(self,
                 name: str,
                 coords: SkyCoord,
                 diam: Quantity = None,
                 height: Quantity = None,
                 width: Quantity = None,
                 serial: int = None):

        if diam is None and (height is None or width is None):
            raise ValueError("You must specify 'diam' argument or 'height' and 'width' arguments")
        elif diam is not None:
            if not (height is None and width is None):
                raise ValueError("You cannot specify 'diam' with 'height' or 'width' arguments")
            self.diam = diam
        else:
            if height is None or width is None:
                raise ValueError("You must specify both 'height' and 'width' arguments")
            self.height = height
            self.width = width

        self.name = name
        self.coords = coords
        self.serial = serial

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if isinstance(other, Region):
            return self.name == other.name
        return self.name == f"{other}"

    def __hash__(self) -> int:
        return hash(self.name)
