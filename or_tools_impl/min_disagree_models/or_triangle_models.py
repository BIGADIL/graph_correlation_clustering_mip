from typing import List

from ortools.linear_solver import pywraplp

from abstract_models.min_disagree_model.abstract_model import MDAAbstractModel


class MDAORTriangleModel(MDAAbstractModel):
    def __init__(self,
                 graph: List[List[int]]) -> None:
        super().__init__(graph)
        self.model: pywraplp.Solver = pywraplp.Solver.CreateSolver("SAT")
        self.x = None
        self.pos_part = None
        self.neg_part = None
        self.add_variables()
        self.add_goal()
        self.add_constraints()

    def add_variables(self) -> None:
        self.x = []
        for i in range(self.size):
            row = []
            for j in range(i):
                row.append(self.model.BoolVar("x_" + str(i) + str(j)))
            self.x.append(row)

    def add_goal(self) -> None:
        self.pos_part = self.model.Sum(self.x[i][j] for i in range(self.size) for j in range(i) if self.graph[i][j] == 1)
        self.neg_part = self.model.Sum((1 - self.x[i][j]) for i in range(self.size) for j in range(i) if self.graph[i][j] == 0)
        self.model.Minimize(self.pos_part + self.neg_part)

    def add_constraints(self) -> None:
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    self.model.Add(self.x[i][k] <= self.x[i][j] + self.x[j][k])
                    self.model.Add(self.x[i][j] <= self.x[i][k] + self.x[j][k])
                    self.model.Add(self.x[j][k] <= self.x[i][j] + self.x[i][k])

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


class MDAORTriangleModelLeqK(MDAORTriangleModel):
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
