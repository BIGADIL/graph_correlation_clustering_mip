import collections
import json
import os
import time
from typing import Dict

from mip_impl.min_disagree_models import *
#from or_tools.min_disagree_models import *


def check_models(models: List[MDAAbstractModel],
                 graph,
                 density,
                 size,
                 optimal_obj_value: int = None) -> Dict:
    result = collections.OrderedDict()
    result["size"] = size
    result["density"] = density
    result["graph"] = graph
    s = set()
    for i in range(len(models)):
        model = models[i]
        start = time.time()
        model.optimize()
        com_time = time.time() - start
        obj_value = model.objective_value()
        s.add(obj_value)
        d = collections.OrderedDict()
        clustering_vector = model.get_clustering_vector()
        d["clustering_vector"] = clustering_vector
        d["objective function value"] = obj_value
        d["computation time seconds"] = com_time
        result[model.get_name()] = d
        if optimal_obj_value is not None and obj_value != optimal_obj_value:
            msg = f"Expected={optimal_obj_value}, actual={obj_value}"
            raise AssertionError(msg)
    if len(s) != 1:
        raise AssertionError("Mismatch objective value")
    return result


NAME = "k-2-n-25-p-0.330000"
path_to_data = os.path.join("data", NAME + ".json")
path_to_res = os.path.join("output", NAME + "-result.json")

if __name__ == "__main__":
    with open(path_to_data, 'r') as f_json:
        data = json.load(f_json)
    if not os.path.isfile(path_to_res) or os.stat(path_to_res).st_size == 0:
        res = []
    else:
        with open(path_to_res, 'r') as res_json:
            res = json.load(res_json)
    for i in range(len(res), len(data)):
        d = data[i]
        models = [
            MDAMIPIneqModelLeqK(graph=d["graph"], k=2),
            MDAMIPTriangleModelLeqK(graph=d["graph"], k=2),
            MDAMIPModuleModel(graph=d["graph"], k=2),
        ]
        d_result = check_models(
            models,
            d["graph"],
            d["density"],
            d["size"],
            d["BranchAndBounds"]["objective function value"]
        )
        res.append(d_result)
        with open(path_to_res, 'w') as res_json:
            res_json.write("[\n")
            for j in range(len(res)):
                for_dump = res[j]
                s = json.dumps(for_dump)
                res_json.write(s)
                if j == len(res) - 1:
                    res_json.write("\n]")
                else:
                    res_json.write(",\n")
