from typing import List

from mip import BINARY, xsum, Model, MINIMIZE

from abstract_models.min_disagree_model.abstract_model import MDAAbstractModel


class MDAMIPModuleModel(MDAAbstractModel):
    def __init__(self,
                 graph: List[List[int]],
                 k: int = None,
                 solver_name: str = "cbc",
                 threads: int = -1) -> None:
        super().__init__(graph)
        self.k = k if k is not None else self.size
        self.model = Model(sense=MINIMIZE, solver_name=solver_name)
        self.model.threads = threads
        self.x = None
        self.u = None
        self.v = None
        self.pos_part = None
        self.neg_part = None
        self.add_variables()
        self.add_goal()
        self.add_constraints()

    def add_variables(self) -> None:
        if self.k == 2:
            self.add_variables_for_k_2()
        else:
            self.add_variables_for_k_geq_3()

    def add_variables_for_k_2(self) -> None:
        self.x = []
        self.x.append(0)
        self.u = []
        self.v = []
        for i in range(1, self.size):
            self.x.append(self.model.add_var(var_type=BINARY))
        for i in range(self.size):
            row_u = []
            row_v = []
            for j in range(i):
                if j == 0:
                    row_u.append(None)
                    row_v.append(None)
                else:
                    row_u.append(self.model.add_var(var_type=BINARY))
                    row_v.append(self.model.add_var(var_type=BINARY))
            self.u.append(row_u)
            self.v.append(row_v)

    def add_variables_for_k_geq_3(self):
        self.x = []
        self.x.append(0)
        self.u = []
        self.v = []
        for _ in range(1, self.size):
            row_x = []
            for _ in range(self.k):
                row_x.append(self.model.add_var(var_type=BINARY))
            self.x.append(row_x)
        for i in range(self.size):
            row_u = []
            row_v = []
            for j in range(i):
                if j == 0:
                    col_u = None
                    col_v = None
                else:
                    col_u = []
                    col_v = []
                    for _ in range(self.k):
                        col_u.append(self.model.add_var(var_type=BINARY))
                        col_v.append(self.model.add_var(var_type=BINARY))
                row_u.append(col_u)
                row_v.append(col_v)
            self.u.append(row_u)
            self.v.append(row_v)

    def add_goal(self) -> None:
        if self.k == 2:
            self.add_goal_for_k_2()
        else:
            self.add_goal_for_k_geq_3()

    def add_goal_for_k_2(self):
        x_pos = []
        x_neg = []
        for i in range(self.size):
            for j in range(i):
                if j == 0:
                    if self.graph[i][j] == 1:
                        x_pos.append(self.x[i])
                    else:
                        x_neg.append(1 - self.x[i])
                else:
                    if self.graph[i][j] == 1:
                        x_pos.append(self.u[i][j] + self.v[i][j])
                    else:
                        x_neg.append(self.u[i][j] + self.v[i][j])
        self.pos_part = xsum(x_neg)
        self.neg_part = xsum(x_pos)
        self.model.objective += self.pos_part + self.neg_part

    def add_goal_for_k_geq_3(self):
        x_pos = []
        x_neg = []
        const = 0
        for i in range(self.size):
            for j in range(i):
                if j == 0:
                    if self.graph[i][j] == 1:
                        x_pos.append(1 - self.x[i][0])
                    else:
                        x_neg.append(self.x[i][0])
                else:
                    buffer = []
                    for r in range(self.k):
                        buffer.append(self.u[i][j][r] + self.v[i][j][r])
                    if self.graph[i][j] == 1:
                        x_pos.append(0.5 * xsum(buffer))
                    else:
                        x_neg.append(0.5 * xsum(buffer))
                        const += 0.5 * (self.k - 2)
        self.pos_part = xsum(x_neg)
        self.neg_part = xsum(x_pos)
        self.model.objective += self.pos_part + self.neg_part - const

    def add_constraints(self) -> None:
        if self.k == 2:
            self.add_constraints_for_k_2()
        else:
            self.add_constraints_for_k_geq_3()

    def add_constraints_for_k_2(self):
        for i in range(self.size):
            for j in range(i):
                if j == 0:
                    continue
                if self.graph[i][j] == 1:
                    self.model += self.x[i] - self.x[j] + self.u[i][j] - self.v[i][j] == 0
                else:
                    self.model += self.x[i] + self.x[j] - 1 + self.u[i][j] - self.v[i][j] == 0

    def add_constraints_for_k_geq_3(self):
        for i in range(1, self.size):
            self.model += xsum(self.x[i]) == 1
            for j in range(1, i):
                for r in range(self.k):
                    if self.graph[i][j] == 1:
                        self.model += self.x[i][r] - self.x[j][r] + self.u[i][j][r] - self.v[i][j][r] == 0
                    else:
                        self.model += self.x[i][r] + self.x[j][r] - 1 + self.u[i][j][r] - self.v[i][j][r] == 0

    def get_clustering_vector(self):
        if self.k == 2:
            return self.get_clustering_vector_for_k_2()
        else:
            return self.get_clustering_vector_for_k_geq_3()

    def get_clustering_vector_for_k_2(self):
        res = [-1] * self.size
        res[0] = 0
        for i in range(1, self.size):
            res[i] = int(self.x[i].x)
        return res

    def get_clustering_vector_for_k_geq_3(self):
        d = {0: [0]}
        for i in range(1, self.size):
            for r in range(self.k):
                if int(self.x[i][r].x) == 1:
                    if r in d:
                        d[r].append(i)
                    else:
                        d[r] = [i]
        res = [-1] * self.size
        n = 0
        for key in d:
            data = d[key]
            for idx in data:
                res[idx] = n
            n += 1
        return res

    def write_as_mps(self, path):
        self.model.write(path + ".mps")

    def optimize(self) -> None:
        self.model.optimize()

    def objective_value(self) -> int:
        if self.model.objective_value is None:
            raise Exception("Not calculated obj value")
        return int(self.model.objective_value)
