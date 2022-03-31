#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
from modules.make_names import make_names
from modules.collect_name_styles import collect_name_styles
from classes.keyword_class import Keyword
from typing import List
from modules.convert_excel_to_json import convert_excel_to_json
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.generate_hard_lemma import generate_hard_lemma

# Pandas input/output for prototype only: remove for production
import pandas as pd

# "dictionary_fp" input is a filepath
def pull_dictionary(dictionary_fp: str, keyword_type: str) -> List[Keyword]:

    with open(dictionary_fp) as dictionary_file:
        dictionary_data = json.loads(dictionary_file.read())

    target_list = []
    for data in dictionary_data:
        if data["shortlist"] is not None and data["shortlist"] != "":
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
                    pairing_limitations=data["pairing_limitations"],
                    shortlist=data["shortlist"]
                )
        )
    return target_list

# Generate name ideas
# "keyword_fp", "name_style_fp", "json_output_fp", "xlsx_output_fp" inputs are filepaths
def generate_names(keyword_fp: str, name_style_fp: str, json_output_fp: str):

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

    keyword_shortlist = generate_keyword_shortlist(keyword_data)

    for keyword_obj in keyword_shortlist:

            if keyword_obj.pos == "noun":
                nouns.append(keyword_obj)
            elif keyword_obj.pos == "verb":
                verbs.append(keyword_obj)
            elif keyword_obj.pos == "adjective":
                adjectives.append(keyword_obj)
            elif keyword_obj.pos == "adverb":
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
        out_file.write(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    shortlisted_names = {}

    for key, name in all_names.items():
        if name.shortlist == "yes":
            shortlisted_names[key] = name

    json_sl_output_fp = json_output_fp.replace("/", "/shortlisted_")

    with open(json_sl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(shortlisted_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    

    # Excel output for prototype only: for production, remove code below
    xlsx_output_fp = json_output_fp.replace(".json", ".xlsx")
    excel_output = []
    name_in_lower_previous = ""
    for key_1, name in all_names.items():

        for key_2, etymology in name.etymologies.items():

            if name_in_lower_previous == name.name_in_lower:
                name_lowercase = ""
            else:
                name_lowercase = name.name_in_lower

            excel_output.append(
                {
                    "name lowercase": name_lowercase,
                    "name titlecase": etymology.name_in_title,
                    "length": name.length,
                    "length score": name.length_score,
                    "total score": name.total_score,
                    "phonetic pattern": int(name.phonetic_pattern),
                    "phonetic count": name.phonetic_count,
                    "plausible word?": name.word_plausibility,
                    "is it a word?": name.is_word,
                    "shortlist": name.shortlist,
                    "keywords": etymology.keywords,
                    "name styles": etymology.name_styles,
                }
            )

            name_in_lower_previous = name_lowercase

    excel_output = sorted(excel_output, key=lambda d: d["name titlecase"].lower())
    excel_output = sorted(excel_output, key=lambda d: d["length"])
    excel_output = sorted(excel_output, key=lambda d: d["total score"], reverse=True)

    df1 = pd.DataFrame.from_dict(excel_output, orient="columns")
    df1.to_excel(xlsx_output_fp)

if __name__ == "__main__":
    generate_names(sys.argv[1], sys.argv[2], sys.argv[3])
