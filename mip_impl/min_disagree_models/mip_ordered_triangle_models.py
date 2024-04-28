from typing import List

from mip import BINARY, xsum, Model, MINIMIZE

from abstract_models.min_disagree_model.abstract_model import MDAAbstractModel


class MDAMIPOrderedTriangleModel(MDAAbstractModel):
    def __init__(self,
                 graph: List[List[int]],
                 solver_name: str = "cbc",
                 threads: int = -1) -> None:
        super().__init__(graph)
        self.model = Model(sense=MINIMIZE, solver_name=solver_name)
        self.model.threads = threads
        self.x = None
        self.pos_part = None
        self.neg_part = None
        self.add_variables()
        self.add_goal()
        self.add_constraints()

    def add_variables(self) -> None:
        self.x = []
        self.x = [[self.model.add_var(var_type=BINARY) for _ in range(self.size)] for _ in range(self.size)]

    def add_goal(self) -> None:
        self.pos_part = xsum(
            self.x[i][j] for i in range(self.size) for j in range(self.size) if self.graph[i][j] == 1 and i != j)
        self.neg_part = xsum(
            (1 - self.x[i][j]) for i in range(self.size) for j in range(self.size) if self.graph[i][j] == 0 and i != j)
        self.model.objective = (self.pos_part + self.neg_part) / 2

    def optimize(self) -> None:
        self.model.optimize()

    def objective_value(self) -> int:
        if self.model.objective_value is None:
            raise Exception("Not calculated obj value")
        return int(self.model.objective_value)

    def add_constraints(self) -> None:
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    if i == j or i == k or j == k:
                        continue
                    self.model += self.x[i][k] <= self.x[i][j] + self.x[j][k]


class MDAMIPOrderedTriangleModelLeqK(MDAMIPOrderedTriangleModel):
    def __init__(self,
                 graph: List[List[int]],
                 k: int,
                 solver_name: str = "cbc",
                 threads: int = -1) -> None:
        self.k = k
        super().__init__(graph, solver_name, threads)

    def add_constraints(self):
        super().add_constraints()
        if self.k == 2:
            self.add_constraints_for_k_2()
        elif self.k == 3:
            self.add_constraints_for_k_3()
        else:
            raise Exception(f"Unsupported k = {self.k}")

    def add_constraints_for_k_2(self):
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    if i == j or i == k or j == k:
                        continue
                    self.model += self.x[i][j] + self.x[i][k] + self.x[j][k] <= 2

    def add_constraints_for_k_3(self):
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    for r in range(self.size):
                        if i == j or i == k or j == k or i == r or j == r or k == r:
                            continue
                        self.model += self.x[i][j] + self.x[i][k] + self.x[i][r] + self.x[j][k] + self.x[j][r] + self.x[k][r] <= 5
