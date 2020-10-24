from abc import abstractmethod
from typing import Dict, TypeVar

from ..models import Region

Catalogue = TypeVar('Catalogue', bound=Dict[str, Region])


class BaseCatalogue:
    """
    Base class to define catalogues.

    This is a pure virtual class which does not implement any method
    but declares methods that every child class must implement.

    Raises:
        NotImplementedError: Every method of this class raises this exception.
    """
    @staticmethod
    @abstractmethod
    def load_catalogue() -> Catalogue:
        """
        Static method for loading the catalogue.
        """
        raise NotImplementedError
