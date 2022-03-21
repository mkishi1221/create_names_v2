#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
from modules.make_names import make_names
from modules.collect_algorithms import collect_algorithms
from classes.algorithm import Algorithm
import pandas as pd
from classes.keyword import Keyword
from typing import List

# "dictionary_file" input is a filepath
def pull_dictionary(dictionary_file: str, keyword_type: str) -> List[Keyword]:
    df = pd.read_excel(dictionary_file, index_col=0)
    final_df = df[df["Keyword shortlist (insert \"s\")"] == "s"]
    final_df = final_df.fillna('')
    target_list = []
    for index, row in final_df.iterrows():
        target_list.append(
            Keyword(
                origin="dictionary",
                source_word="",
                spacy_lemma="",
                keyword=row["keyword"],
                keyword_len=row["keyword_len"],
                spacy_pos="",
                wordsAPI_pos="",
                pos=keyword_type,
                spacy_occurrence="",
                pairing_limitations=row["pairing_limitations"]
            )
        )
    return target_list

# Generate name ideas
# "keyword_file" input is a filepath
# "algorithm_file" input is a filepath
# "tmp_output" input is a filepath
# "output" input is a filepath
def generate_names(keyword_file: str, algorithm_file: str, tmp_output: str, output: str):

    # Get all algorithms
    algorithms = collect_algorithms(algorithm_file)
    comp_list_types = []
    required_comps = []

    for algo in algorithms:
        comp_list_type = sorted([component.keyword_type for component in algo.components])
        if comp_list_type not in comp_list_types:
            comp_list_types.append(comp_list_type)

    # Get all elements used in comp_list
    for comp_list_type in comp_list_types:
        for comp in comp_list_type:
            if comp not in required_comps:
                required_comps.append(comp)

    # Access keyword list and sort words into verbs, nouns or adjectives
    df = pd.read_excel(keyword_file, index_col=0)
    keyword_df = df[df["Keyword shortlist (insert \"s\")"] == "s"]
    keyword_df = keyword_df.fillna('')
    verbs = []
    nouns = []
    adjectives = []

    for index, row in keyword_df.iterrows():
        keyword_obj = Keyword(
            origin=row["origin"],
            source_word=row["source_word"],
            spacy_lemma=row["spacy_lemma"],
            keyword=row["keyword"],
            keyword_len=row["keyword_len"],
            spacy_pos=row["spacy_pos"],
            wordsAPI_pos=row["wordsAPI_pos"],
            pos=row["pos"],
            spacy_occurrence=row["spacy_occurrence"],
            pairing_limitations=row["pairing_limitations"]
        )

        if row["wordsAPI_pos"] == "noun":
            nouns.append(keyword_obj)
        elif row["wordsAPI_pos"] == "verb":
            verbs.append(keyword_obj)
        elif row["wordsAPI_pos"] == "adjective":
            adjectives.append(keyword_obj)

    # Pull required dictionaries
    if "pref" in required_comps:
        prefix_file = "dict/prefix.xlsx"
        keyword_type = "prefix"
        prefixes = pull_dictionary(prefix_file, keyword_type)
    else:
        prefixes = []

    if "suff" in required_comps:
        suffix_file = "dict/suffix.xlsx"
        keyword_type = "suffix"
        suffixes = pull_dictionary(suffix_file, keyword_type)
    else:
        suffixes = []

    # these lists will be added later
    joints = []
    heads = []
    tails = []

    # Add all lists into dict form
    keyword_dict = {
        "verb": verbs,
        "noun": nouns,
        "adje": adjectives,
        "pref": prefixes,
        "suff": suffixes,
        "join": joints,
        "head": heads,
        "tail": tails,
    }

    with open("tmp/keyword_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict, option=json.OPT_INDENT_2))

    # Generate names
    all_names = make_names(algorithms, keyword_dict)

    with open(tmp_output, "wb+") as out_file:
        # remove below indent when no further debug needed for more speeeeeed
        out_file.write(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    excel_output = []

    for name_key, names_list in all_names.items():
        for name in names_list:
            excel_output.append(name)

    excel_output = sorted(excel_output, key=lambda d: d.name_lower)
    excel_output = sorted(excel_output, key=lambda d: d.length)
    excel_output = sorted(excel_output, key=lambda d: d.total_score, reverse=True)

    # Export to excel file
    df1 = pd.DataFrame.from_dict(excel_output, orient="columns")
    df1.to_excel(output)

if __name__ == "__main__":
    generate_names(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
