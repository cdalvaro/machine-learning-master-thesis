from abc import abstractmethod
from typing import Dict, TypeVar

from ..info import Cluster

Catalogue = TypeVar('Catalogue', bound=Dict[str, Cluster])


class BaseCatalogue:

    @staticmethod
    @abstractmethod
    def load_catalogue() -> Catalogue:
        """
        Static method for loading the selected catalogue
        """
        raise NotImplementedError
