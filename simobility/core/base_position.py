from typing import Tuple, Dict
import json
from abc import ABC, abstractmethod
from uuid import uuid4


class BasePosition(ABC):
    """Defines interface for positions from different coordinate systems, e.g.
    latitude and longiture, grid cells. Each position must implement method
    for calculating distance between two position and method for comparing
    two coordinates.
    """

    def __init__(self):
        self.id = uuid4().hex

    @abstractmethod
    def distance(self, pos) -> float:
        pass

    @property
    @abstractmethod
    def coords(self) -> Tuple:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return json.dumps(self.to_dict())
