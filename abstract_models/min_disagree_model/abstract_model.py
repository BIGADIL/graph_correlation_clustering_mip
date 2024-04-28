from abc import ABC
from typing import List


class MDAAbstractModel(ABC):
    def __init__(self,
                 graph: List[List[int]]) -> None:
        """

        :param graph:
        """
        self.graph = graph
        self.size = len(graph)

    def optimize(self) -> None:
        raise AttributeError("Not implement yet")

    def objective_value(self) -> int:
        raise AttributeError("Not implement yet")

    def get_clustering_vector(self):
        raise AttributeError("Not implement yet")

    @classmethod
    def get_name(cls):
        return cls.__name__
