#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
import copy
import pandas as pd
from pattern3.text.en import pluralize
import dataclasses
from classes.keyword_class import Keyword
from classes.keyword_class import Preferred_Keyword
from modules.collect_algorithms import collect_algorithms
from modules.convert_excel_to_json import convert_excel_to_json
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.find_contained_words import find_contained_words
from modules.process_user_keywords import process_user_keywords_dict
from modules.verify_words_with_eng_dict import verify_words_with_eng_dict
from modules.pull_user_keyword_bank import pull_user_keyword_bank
from modules.keyword_modifier import keyword_modifier
from modules.grade_phonetic import grade_phonetic
from modules.manage_contained_words import pull_master_exempt


def process_additional_keywords(additional_keyword_list_fp, project_path, master_exempt_contained_words):
    keywords_json_fp = f"{project_path}/tmp/keyword_generator/additional_keywords.json"
    keywords_json_fp = convert_excel_to_json(additional_keyword_list_fp, target_sheet="additional keywords", output_json_fp=keywords_json_fp, convert_list=True)
    with open(keywords_json_fp) as keyword_file:
        not_valid = [None, ""]
        additional_keyword_list = [ kw_obj for kw_obj in json.loads(keyword_file.read()) if kw_obj["keyword"] not in not_valid and kw_obj["disable"] in not_valid ]
    if len(additional_keyword_list) != 0:
        print("Extracting keywords from keyword list and processing them through spacy......")
        additional_keywords = process_user_keywords_dict(additional_keyword_list, project_path)
        for keyword in additional_keywords:
            keyword.origin = ["additional_user_keywords"]
        print("Getting keyword pos using eng_dict dictionary......")
        additional_keywords = verify_words_with_eng_dict(additional_keywords, project_path, master_exempt_contained_words)
    else:
        additional_keywords = []
    return additional_keywords

def isNone(variable):
    if len(variable) == 0 or variable == "" or variable == None:
        result = None
    else:
        result = variable
    return result

# Generate name ideas
# "keyword_fp", "algorithm_fp", "json_output_fp", "xlsx_output_fp" inputs are filepaths
def generate_modwords(project_id: str):

    project_path = f"projects/{project_id}"

    # input file filepaths and filenames:
    keyword_fp = f"{project_path}/results/{project_id}_keywords.xlsx"

    # tmp file filepaths and filenames:
    keyword_dict_json_fp = f"{project_path}/tmp/keyword_generator/{project_id}_keyword_dict.json"
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp = f"{project_path}/results/{project_id}_modwords.xlsx"

    # Pull master exempt contained words list
    master_exempt_contained_words = pull_master_exempt()
    curated_eng_word_list = set(open("name_generator/curated_eng_word_list.txt", "r").read().splitlines())

    # Get all algorithms
    print("Loading algorithms...")
    algorithms = collect_algorithms()
    modifier_list = set()

    sheet_names = ["nouns", "verbs", "adjectives", "adverbs"]
    pos_list = ["noun", "verb", "adjective", "adverb"]
    for algorithm in algorithms:
        for component in algorithm.components:
            modifier_list.add(component.modifier)

    # Access keyword list and sort words into verbs, nouns or adjectives
    # Excel input for prototype only: for production, import directly from json
    keyword_dict = {}
    for pos in pos_list:
        keyword_dict[pos] = []

    keywords_json_fp = convert_excel_to_json(keyword_fp, target_sheets=sheet_names, output_json_fp=keywords_json_fp, convert_list=True)
    with open(keywords_json_fp) as keyword_file:
        keyword_data = json.loads(keyword_file.read())
    raw_keyword_shortlist = generate_keyword_shortlist(keyword_data) + process_additional_keywords(keyword_fp, project_path, master_exempt_contained_words)
    user_keyword_bank_list = pull_user_keyword_bank(project_path)
    keyword_shortlist = []
    for keyword_obj in raw_keyword_shortlist:
        key = Preferred_Keyword(keyword=keyword_obj.keyword)
        if key in user_keyword_bank_list:
            kw_index = user_keyword_bank_list.index(key)
            pos_list = user_keyword_bank_list[kw_index].preferred_pos
            for pos_str in pos_list:
                keyword_obj = copy.deepcopy(keyword_obj)
                keyword_obj.pos = pos_str
                keyword_obj.preferred_pos = pos_list
                keyword_obj.keyword_class = "prime"
                if keyword_obj not in keyword_shortlist:
                    keyword_shortlist.append(keyword_obj)
        elif keyword_obj not in keyword_shortlist:
            keyword_shortlist.append(keyword_obj)

    print("Fetching keywords and making modifications...")
    if len(keyword_shortlist) == 0:
        print("No keywords shortlisted!")
        exit()

    for keyword_obj in keyword_shortlist:
        pos = keyword_obj.pos
        for kw_modifier in modifier_list:
            modword_list = keyword_modifier(keyword_obj, kw_modifier)
            if modword_list is not None:
                for modword_obj in modword_list:
                    keyword_dict[pos].append(modword_obj)

        # Generate plural:
        if pos == "noun":
            plural_noun_str = pluralize(keyword_obj.keyword)
            if plural_noun_str[-2:] != "ss":
                keyword_obj: Keyword = copy.deepcopy(keyword_obj)
                keyword_obj.keyword = plural_noun_str
                keyword_obj.pos = "plural_noun"
                keyword_obj.phonetic_grade, keyword_obj.phonetic_pattern = grade_phonetic(plural_noun_str)
                keyword_obj.contained_words = find_contained_words(keyword=plural_noun_str, curated_eng_list=curated_eng_word_list, type="keyword", exempt=master_exempt_contained_words)
                keyword_obj.keyword_class = "prime"
                for kw_modifier in modifier_list:
                    modword_list = keyword_modifier(keyword_obj, kw_modifier)
                    if modword_list is not None:
                        for modword_obj in modword_list:
                            keyword_dict[pos].append(modword_obj)

    desired_order_list = [
        "origin",
        "source_word",
        "spacy_pos",
        "eng_dict_pos",
        "keyword_len",
        "contained_words",
        "phonetic_pattern",
        "phonetic_grade",
        "components",
        "abbreviations",
        "yake_rank",
        "modifier",
        "modword_len",
        "pos",
        "keyword",
        "modword",
        "example_front",
        "example_back",
        "shortlist",
    ]

    keyword_dict_json = {}
    keyword_dict_keys = set()
    for key, keyword_list in keyword_dict.items():
        keyword_list = sorted(list(keyword_list), key=lambda d: (d.keyword_len, d.keyword, d.modword_len))
        for kw_obj in keyword_list:
            pos_str = kw_obj.pos
            key_str = f"{kw_obj.keyword}|{kw_obj.modword}"
            example_front_str = f"Word{kw_obj.modword.title()}"
            example_back_str = f"{kw_obj.modword.title()}Word"
            kw_obj = dataclasses.asdict(kw_obj)
            kw_obj["pos"] = [pos_str]
            kw_obj["example_front"] = example_front_str
            kw_obj["example_back"] = example_back_str
            reordered_dict = {key: kw_obj[key] for key in desired_order_list}
            if key_str not in keyword_dict_keys:
                keyword_dict_json[key_str] = reordered_dict
                keyword_dict_keys.add(key_str)
            else:
                keyword_dict_json[key_str]["pos"].append(pos_str)

    with open(keyword_dict_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict_json, option=json.OPT_INDENT_2))

    print(f"Exporting {project_id}_modwords.xlsx...")
    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')
    keyword_list = list(keyword_dict_json.values())
    df = pd.DataFrame.from_dict(keyword_list, orient="columns")
    list_len = len(keyword_list)
    sheet_name_str = f"Modwords ({list_len})"
    df.to_excel(writer, sheet_name=sheet_name_str)
    workbook  = writer.book
    worksheet = writer.sheets[sheet_name_str]
    worksheet.set_column(1, 20, 15)
    writer.save()

if __name__ == "__main__":
    generate_modwords(sys.argv[1])
