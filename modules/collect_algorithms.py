from classes.algorithm import Algorithm
import pandas as pd

def collect_algorithms(algorithm_file):

    # Import algorithm list from xlsx file
    df = pd.read_excel(algorithm_file, index_col=0)
    algorithm_df = df[df["deactivate"].isna()]

    algorithms = set()

    for index, row in algorithm_df.iterrows():
        comp_list = []
        if str(row["keyword_type_1"]) != "nan":
            comp_list.append((row["keyword_type_1"], row["modifier_1"]))
        if str(row["keyword_type_2"]) != "nan":
            comp_list.append((row["keyword_type_2"], row["modifier_2"]))
        if str(row["keyword_type_3"]) != "nan":
            comp_list.append((row["keyword_type_3"], row["modifier_3"]))

        algorithms.add(Algorithm(0, comp_list))

    return algorithms
