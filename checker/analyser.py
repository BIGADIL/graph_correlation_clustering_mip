import json
import os
import statistics

from or_tools_impl.min_disagree_models import *

NAME = "k-2-n-20-p-0.330000"
path_to_res = os.path.join("output", NAME + "-result.json")

if __name__ == "__main__":
    with open(path_to_res, 'r') as f_json:
        data = json.load(f_json)
        models = [
            MDAORIneqModelLeqK.get_name(),
            MDAORTriangleModelLeqK.get_name(),
            MDAORModuleModel.get_name(),
            # MDAORUnorderedOneHotModel.get_name()
        ]
        d = {}
        for model in models:
            d[model] = []
        for i in range(len(data)):
            sol = data[i]
            for model in models:
                d[model].append(sol[model]["computation time seconds"])
        for key in d:
            value = d[key]
            print(key, "median = ", statistics.median(value), "mean = ", statistics.mean(value), "std = ", statistics.stdev(value))