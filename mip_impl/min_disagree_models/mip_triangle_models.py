from typing import List

from mip import BINARY, xsum, Model, MINIMIZE

from abstract_models.min_disagree_model.abstract_model import MDAAbstractModel


class MDAMIPTriangleModel(MDAAbstractModel):
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
        for i in range(self.size):
            row = [self.model.add_var(var_type=BINARY) for _ in range(i)]
            self.x.append(row)

    def add_goal(self) -> None:
        self.pos_part = xsum(self.x[i][j] for i in range(self.size) for j in range(i) if self.graph[i][j] == 1)
        self.neg_part = xsum((1 - self.x[i][j]) for i in range(self.size) for j in range(i) if self.graph[i][j] == 0)
        self.model.objective = self.pos_part + self.neg_part

    def add_constraints(self) -> None:
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    self.model += self.x[i][k] <= self.x[i][j] + self.x[j][k]
                    self.model += self.x[i][j] <= self.x[i][k] + self.x[j][k]
                    self.model += self.x[j][k] <= self.x[i][j] + self.x[i][k]

    def optimize(self) -> None:
        self.model.optimize()

    def objective_value(self) -> int:
        if self.model.objective_value is None:
            raise Exception("Not calculated obj value")
        return int(self.model.objective_value)

    def get_clustering_vector(self):
        d = {}
        result = [-1] * self.size
        for i in range(self.size):
            d[i] = [i]
        for i in range(self.size):
            for j in range(i):
                if int(self.x[i][j].x) == 0:
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

    def write_as_mps(self, path):
        self.model.write(path + ".mps")


class MDAMIPTriangleModelLeqK(MDAMIPTriangleModel):
    def __init__(self,
                 graph: List[List[int]],
                 k: int,
                 solver_name: str = "cbc",
                 threads: int = -1) -> None:
        self.k = k
        super().__init__(graph, solver_name, threads)

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
                    self.model += self.x[i][j] + self.x[i][k] + self.x[j][k] <= 2

    def add_constraints_for_k_3(self):
        for i in range(self.size):
            for j in range(i):
                for k in range(j):
                    for r in range(k):
                        self.model += self.x[i][j] + self.x[i][k] + self.x[i][r] + self.x[j][k] + self.x[j][r] + self.x[k][r] <= 5
