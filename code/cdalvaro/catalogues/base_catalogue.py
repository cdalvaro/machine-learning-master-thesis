from abc import abstractmethod
from typing import Dict, TypeVar

from ..models import Region

Catalogue = TypeVar('Catalogue', bound=Dict[str, Region])


class BaseCatalogue:
    @staticmethod
    @abstractmethod
    def load_catalogue() -> Catalogue:
        """
        Static method for loading the selected catalogue
        """
        # TODO: Add parameter to fill incomplete fields
        raise NotImplementedError
