#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.algorithm_class import Algorithm
from classes.algorithm_class import Component
import orjson as json
from typing import List

def exchange_comp(comp):

    no_cut_comps = ["no_cut_5", "no_cut_3"]
    if comp in no_cut_comps:
        value = "no_cut"
    else:
        value = comp

    return value

# Input is a file path
def collect_algorithms(algorithms_fp: str) -> List[Algorithm]:

    # Import Algorithm list from xlsx file
    with open(algorithms_fp) as algorithms_file:
        algorithm_data = json.loads(algorithms_file.read())

    algorithms = set()

    for algorithm in algorithm_data:
        if algorithm["deactivate"] == "":
            comp_list = []
            if algorithm["pos_1"] != "":
                comp_list.append(Component(pos=algorithm["pos_1"], modifier=exchange_comp(algorithm["modifier_1"])))
            if algorithm["pos_2"] != "":
                comp_list.append(Component(pos=algorithm["pos_2"], modifier=exchange_comp(algorithm["modifier_2"])))
            if algorithm["pos_3"] != "":
                comp_list.append(Component(pos=algorithm["pos_3"], modifier=exchange_comp(algorithm["modifier_3"])))

            algorithms.add(
                Algorithm(
                    id=0, 
                    components=comp_list
                )
            )

    with open("tmp/name_generator/collected_algorithms.json", "wb+") as out_file:
        out_file.write(json.dumps(list(algorithms), option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    return list(algorithms)
