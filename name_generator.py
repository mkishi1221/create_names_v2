#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
from modules.make_names import make_names
from modules.collect_name_styles import collect_name_styles
from classes.keyword_class import Keyword
from typing import List
from modules.convert_excel_to_json import convert_excel_to_json

# Pandas input/output for prototype only: remove for production
import pandas as pd

# "dictionary_fp" input is a filepath
def pull_dictionary(dictionary_fp: str, keyword_type: str) -> List[Keyword]:

    with open(dictionary_fp) as dictionary_file:
        dictionary_data = json.loads(dictionary_file.read())

    target_list = []
    for data in dictionary_data:
        if data["Keyword shortlist (insert \"s\")"] == "s":
            target_list.append(
                Keyword(
                    origin="dictionary",
                    source_word="",
                    spacy_lemma="",
                    keyword=data["keyword"],
                    keyword_len=data["keyword_len"],
                    spacy_pos="",
                    wordsAPI_pos="",
                    pos=keyword_type,
                    spacy_occurrence="",
                    pairing_limitations=data["pairing_limitations"]
                )
        )
    return target_list

# Generate name ideas
# "keyword_fp", "name_style_fp", "json_output_fp", "xlsx_output_fp" inputs are filepaths
def generate_names(keyword_fp: str, name_style_fp: str, json_output_fp: str, xlsx_output_fp: str):

    # Convert excel file to json file (remove when excel files not used anymore)
    sheet_name = "name_styles"
    name_style_fp = convert_excel_to_json(name_style_fp, sheet_name)

    # Get all name styles
    name_styles = collect_name_styles(name_style_fp)
    comp_list_types = []
    required_comps = []

    for name_style in name_styles:
        comp_list_type = sorted([component.keyword_type for component in name_style.components])
        if comp_list_type not in comp_list_types:
            comp_list_types.append(comp_list_type)

    # Get all elements used in comp_list
    for comp_list_type in comp_list_types:
        for comp in comp_list_type:
            if comp not in required_comps:
                required_comps.append(comp)

    # Access keyword list and sort words into verbs, nouns or adjectives
    # Excel input for prototype only: for production, import directly from json
    sheet_name = "Sheet1"
    keyword_fp = convert_excel_to_json(keyword_fp, sheet_name)   

    with open(keyword_fp) as keyword_file:
        keyword_data = json.loads(keyword_file.read())

    verbs = []
    nouns = []
    adjectives = []
    adverbs = []

    for keyword in keyword_data:

        if keyword["Keyword shortlist (insert \"s\")"] == "s":
            keyword_obj = Keyword(
                origin=keyword["origin"],
                source_word=keyword["source_word"],
                spacy_lemma=keyword["spacy_lemma"],
                keyword=keyword["keyword"],
                keyword_len=keyword["keyword_len"],
                spacy_pos=keyword["spacy_pos"],
                wordsAPI_pos=keyword["wordsAPI_pos"],
                pos=keyword["pos"],
                spacy_occurrence=keyword["spacy_occurrence"],
                pairing_limitations=keyword["pairing_limitations"]
            )

            if keyword["pos"] == "noun":
                nouns.append(keyword_obj)
            elif keyword["pos"] == "verb":
                verbs.append(keyword_obj)
            elif keyword["pos"] == "adjective":
                adjectives.append(keyword_obj)
            elif keyword["pos"] == "adverb":
                adverbs.append(keyword_obj)

    # Pull required dictionaries
    if "pref" in required_comps:
        prefix_file = "dict/prefix.xlsx"
        keyword_type = "prefix"
        sheet_name = "Sheet1"
        prefix_file = convert_excel_to_json(prefix_file, sheet_name)   
        prefixes = pull_dictionary(prefix_file, keyword_type)
    else:
        prefixes = []

    if "suff" in required_comps:
        suffix_file = "dict/suffix.xlsx"
        keyword_type = "suffix"
        sheet_name = "Sheet1"
        suffix_file = convert_excel_to_json(suffix_file, sheet_name)  
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
        "adve": adverbs,
        "pref": prefixes,
        "suff": suffixes,
        "join": joints,
        "head": heads,
        "tail": tails,
    }

    with open("tmp/keyword_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict, option=json.OPT_INDENT_2))

    # Generate names
    all_names = make_names(name_styles, keyword_dict)

    with open(json_output_fp, "wb+") as out_file:
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
    df1.to_excel(xlsx_output_fp)

if __name__ == "__main__":
    generate_names(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
