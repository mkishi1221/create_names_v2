from classes.algorithm import Algorithm
from classes.algorithm import Component
import pandas as pd
from typing import List

# Input is a file path
def collect_algorithms(algorithm_file: str) -> List[Algorithm]:

    # Import algorithm list from xlsx file
    df = pd.read_excel(algorithm_file, index_col=0)
    algorithm_df = df[df["deactivate"].isna()]

    algorithms = set()

    for index, row in algorithm_df.iterrows():
        comp_list = []
        if str(row["keyword_type_1"]) != "nan":
            comp_list.append(Component(keyword_type=row["keyword_type_1"], modifier=row["modifier_1"]))
        if str(row["keyword_type_2"]) != "nan":
            comp_list.append(Component(keyword_type=row["keyword_type_2"], modifier=row["modifier_2"]))
        if str(row["keyword_type_3"]) != "nan":
            comp_list.append(Component(keyword_type=row["keyword_type_3"], modifier=row["modifier_3"]))

        algorithms.add(Algorithm(0, comp_list))

    return list(algorithms)
