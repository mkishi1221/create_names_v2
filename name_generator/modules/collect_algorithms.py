#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.algorithm_class import Algorithm
from classes.algorithm_class import Component
from modules.convert_excel_to_json import convert_excel_to_json
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
def collect_algorithms() -> List[Algorithm]:

    # Import Algorithm list from xlsx file
    algorithm_excel_fp = f"name_generator/dict/algorithms/algorithm_list.xlsx"
    sheet_name = "algorithms"
    algorithm_data, algorithms_fp = convert_excel_to_json(algorithm_excel_fp, target_sheet=sheet_name, convert_list=True)
    algorithms = set()
    for algorithm in algorithm_data:
        not_valid = [None, ""]
        if algorithm["deactivate"] in not_valid:
            comp_list = []
            if algorithm["pos_1"] not in not_valid:
                comp_list.append(Component(pos=algorithm["pos_1"], modifier=exchange_comp(algorithm["modifier_1"])))
            if algorithm["pos_2"] not in not_valid:
                comp_list.append(Component(pos=algorithm["pos_2"], modifier=exchange_comp(algorithm["modifier_2"])))
            if algorithm["pos_3"] not in not_valid:
                comp_list.append(Component(pos=algorithm["pos_3"], modifier=exchange_comp(algorithm["modifier_3"])))

            algorithms.add(
                Algorithm(
                    id=0, 
                    components=comp_list
                )
            )

    return list(algorithms)
