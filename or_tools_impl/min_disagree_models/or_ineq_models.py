from typing import List, Optional

from ortools.linear_solver import pywraplp

from abstract_models.min_disagree_model.abstract_model import MDAAbstractModel


class MDAORIneqModel(MDAAbstractModel):
    def __init__(self,
                 graph: List[List[int]]) -> None:
        super().__init__(graph)
        self.eps = 0.5
        self.M = 10
        self.model: pywraplp.Solver = pywraplp.Solver.CreateSolver("SAT")
        self.x = None
        self.y = None
        self.pos_part = None
        self.neg_part = None
        self.add_variables()
        self.add_goal()
        self.add_constraints()

    def add_variables(self) -> None:
        self.x = []
        for i in range(self.size):
            row = [self.model.BoolVar("x_" + str(i) + str(j)) for j in range(i)]
            self.x.append(row)
        self.y = []
        for i in range(self.size):
            col = []
            for j in range(i):
                row = [self.model.BoolVar("y_" + str(i) + str(j) + str(r)) for r in range(j)]
                col.append(row)
            self.y.append(col)

    def add_goal(self) -> None:
        self.pos_part = self.model.Sum(self.x[i][j] for i in range(self.size) for j in range(i) if self.graph[i][j] == 1)
        self.neg_part = self.model.Sum(
            (1 - self.x[i][j]) for i in range(self.size) for j in range(i) if self.graph[i][j] == 0)
        self.model.Minimize(self.pos_part + self.neg_part)

    def add_constraints(self) -> None:
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    self.model.Add(
                        self.x[i][j] + self.x[i][k] + self.x[j][k] >= 1 + self.eps - (1 - self.y[i][j][k]) * self.M)
                    self.model.Add(
                        self.x[i][j] + self.x[i][k] + self.x[j][k] <= 1 - self.eps + self.y[i][j][k] * self.M)

    def optimize(self) -> None:
        self.model.Solve()

    def objective_value(self) -> int:
        return int(self.model.Objective().Value())

    def get_clustering_vector(self):
        d = {}
        result = [-1] * self.size
        for i in range(self.size):
            d[i] = [i]
        for i in range(self.size):
            for j in range(i):
                if int(self.x[i][j].solution_value()) == 0:
                    d[i].append(j)
                    d[j].append(i)
        for key in d:
            d[key] = tuple(sorted(d[key]))
        seen_clusters = []
        n = 0
        for vector in d.values():
            if vector not in seen_clusters:
                for v in vector:
                    result[v] = n
                n += 1
                seen_clusters.append(vector)
        return result


class MDAORIneqModelLeqK(MDAORIneqModel):
    def __init__(self,
                 graph: List[List[int]],
                 k: int) -> None:
        self.k = k
        super().__init__(graph)

    def add_constraints(self) -> None:
        super().add_constraints()
        if self.k == 2:
            self.add_constraints_for_k_2()
        elif self.k == 3:
            self.add_constraints_for_k_3()
        else:
            raise Exception(f"Unsupported k = {self.k}")

    def add_constraints_for_k_2(self):
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    self.model.Add(self.x[i][j] + self.x[i][k] + self.x[j][k] <= 2)

    def add_constraints_for_k_3(self):
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    for r in range(k):
                        self.model.Add(
                            self.x[i][j] + self.x[i][k] + self.x[i][r] + self.x[j][k] + self.x[j][r] + self.x[k][
                                r] <= 5)
