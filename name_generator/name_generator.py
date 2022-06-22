#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
import os
import copy
import regex as re
from typing import List
from pattern3.text.en import pluralize
import dataclasses
from classes.keyword_class import Keyword
from classes.keyword_class import Modword
from classes.keyword_class import Preferred_Keyword
from classes.name_class import Etymology, Name
from classes.name_class import Graded_name
from modules.make_names import make_names
from modules.collect_algorithms import collect_algorithms
from modules.convert_excel_to_json import convert_excel_to_json
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.find_contained_words import find_contained_words
from modules.pull_wordsAPI import pull_wordsAPI_dict
from modules.process_user_keywords import process_user_keywords_dict
from modules.verify_words_with_wordsAPI import verify_words_with_wordsAPI
from modules.pull_user_keyword_bank import pull_user_keyword_bank
from modules.keyword_modifier import keyword_modifier
from modules.grade_phonetic import grade_phonetic

# Pandas input/output for prototype only: remove for production
import pandas as pd


def process_additional_keywords(additional_keyword_list_fp, project_path):

    keywords_json_fp = f"{project_path}/tmp/name_generator/additional_keywords.json"
    keywords_json_fp = convert_excel_to_json(additional_keyword_list_fp, target_sheet="additional keywords", output_json_fp=keywords_json_fp)
    with open(keywords_json_fp) as keyword_file:
        not_valid = [None, ""]
        additional_keyword_list = [ kw_obj for kw_obj in json.loads(keyword_file.read()) if kw_obj["keyword"] not in not_valid and kw_obj["disable"] in not_valid ]
    if len(additional_keyword_list) != 0:
        print("Extracting keywords from keyword list and processing them through spacy......")
        additional_keywords = process_user_keywords_dict(additional_keyword_list, project_path)
        for keyword in additional_keywords:
            keyword.origin = ["additional_user_keywords"]
        print("Getting keyword pos using wordAPI dictionary......")
        additional_keywords = verify_words_with_wordsAPI(additional_keywords, project_path)
    else:
        additional_keywords = []

    return additional_keywords

def grade_name(name_type, phonetic_grade, non_plausable, is_it_word, name_length, contained_words, if_wiki_title):

    grade_str = None

    if name_type == "cut_name":
        if (
            non_plausable <= 4
            and is_it_word == "no"
            and name_length > 4
            and name_length < 11
            and contained_words == None
            and if_wiki_title == None
        ):
            if phonetic_grade == "Phonetic_A" and non_plausable == 0:
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_B" and non_plausable <= 1:
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_C" and non_plausable <= 2:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
    

    elif name_type == "pref_suff_name":
        if (
            non_plausable <= 4
            and is_it_word == "no"
            and name_length > 4
            and name_length < 11
            and contained_words == None
            and if_wiki_title == None
        ):
            if phonetic_grade == "Phonetic_A":
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_B":
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_C":
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"


    elif name_type == "no_cut_name" or name_type == "text_comp_name":

        if (
            non_plausable <= 4
            and is_it_word == "no"
            and name_length > 4
            and contained_words == None
            and if_wiki_title == None
        ):
            if name_length < 11:
                grade_str = "Grade_A"
            elif name_length < 13:
                grade_str = "Grade_B"
            elif name_length < 17:
                grade_str = "Grade_C"
            elif name_length < 20:
                grade_str = "Grade_D"

    return grade_str

def check_if_wiki_title(is_word, name_in_lower: str, wiki_titles_list: list[str]):

    if is_word == "yes":
        value = f"is_word: {name_in_lower}"
    
    elif len(name_in_lower) > 20:
        value = f"len_over_20: {name_in_lower}"

    elif name_in_lower in wiki_titles_list:
        value = f"yes: {name_in_lower}"
    else:
        value = None

    return value


def isNone(variable):
    if len(variable) == 0 or variable == "" or variable == None:
        result = None
    else:
        result = variable
    return result


# "dictionary_fp" input is a filepath
def pull_dictionary(dictionary_fp: str, pos_str: str) -> List[Keyword]:

    with open(dictionary_fp) as dictionary_file:
        dictionary_data = json.loads(dictionary_file.read())

    target_list = set()
    for data in dictionary_data:
        not_valid = [None, ""]
        if data["shortlist"] not in not_valid:
            target_list.add(
                Modword(
                    origin="dictionary",
                    keyword=data["keyword"],
                    keyword_len=data["keyword_len"],
                    pos=pos_str,
                    restrictions_before=isNone(data["restrictions_before"].replace(",","").split()),
                    restrictions_after=isNone(data["restrictions_after"].replace(",","").split()),
                    restrictions_as_joint=isNone(data["restrictions_as_joint"].replace(",","").split()),
                    shortlist=data["shortlist"],
                    modword=data["keyword"],
                    modword_len=data["keyword_len"],
                )
        )
    return list(target_list)

# Generate name ideas
# "keyword_fp", "algorithm_fp", "json_output_fp", "xlsx_output_fp" inputs are filepaths
def generate_names(project_id: str):

    project_path = f"projects/{project_id}"

    # input file filepaths and filenames:
    keyword_fp = f"{project_path}/results/{project_id}_keywords.xlsx"
    previous_domain_output_fp = f"{project_path}/results/{project_id}_domains.json"

    # dict resource paths and filenames:
    text_components_data_xlsx_fp = "name_generator/dict/text_components.xlsx"
    wiki_titles_data_fp = "../wikipedia_extract_titles/results/wiki_titles_combined_list_filtered.tsv"

    # tmp file filepaths and filenames:
    required_comps_tsv_fp = f"{project_path}/tmp/name_generator/{project_id}_comps.tsv"
    keyword_dict_json_fp = f"{project_path}/tmp/name_generator/{project_id}_keyword_dict.json"
    json_ungraded_output_fp = f"{project_path}/tmp/name_generator/{project_id}_ungraded_names.json"
    json_graded_output_fp = f"{project_path}/tmp/name_generator/{project_id}_graded_names.json"
    remaining_shortlist_json_fp = f"{project_path}/tmp/name_generator/{project_id}_remaining_shortlist.json"
    json_sl_output_fp = f"{project_path}/tmp/name_generator/{project_id}_names_shortlist.json"
    json_stats_output_fp = f"{project_path}/tmp/name_generator/{project_id}_names_raw_stats.json"
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp = f"{project_path}/results/{project_id}_names.xlsx"

    # Get all algorithms
    print("Loading algorithms...")
    raw_algorithms = collect_algorithms()
    required_comps = {}

    for algorithm in raw_algorithms:
        for component in algorithm.components:
            if component.pos not in required_comps.keys():
                required_comps[component.pos] = {component.modifier}
            elif component.modifier not in required_comps[component.pos]:
                required_comps[component.pos].add(component.modifier)

    with open(required_comps_tsv_fp, "wb+") as out_file:
        out_file.write(str(required_comps).encode())

    # Access keyword list and sort words into verbs, nouns or adjectives
    # Excel input for prototype only: for production, import directly from json
    keyword_dict = {}
    pos_conversion = {
        "adjective": "adje",
        "adverb": "advb",
    }
    for pos, modifier_list in required_comps.items():
        for kw_modifier in modifier_list:
            if pos in pos_conversion.keys():
                pos = pos_conversion[pos]
            key = f"{pos}|{kw_modifier}"
            keyword_dict[key] = set()

    sheets = ["nouns", "verbs", "adjectives", "adverbs"]
    keywords_json_fp = convert_excel_to_json(keyword_fp, target_sheets=sheets, output_json_fp=keywords_json_fp)
    with open(keywords_json_fp) as keyword_file:
        keyword_data = json.loads(keyword_file.read())
    raw_keyword_shortlist = generate_keyword_shortlist(keyword_data) + process_additional_keywords(keyword_fp, project_path)
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
                if keyword_obj not in keyword_shortlist:
                    keyword_shortlist.append(keyword_obj)
        elif keyword_obj not in keyword_shortlist:
            keyword_shortlist.append(keyword_obj)

    print("Fetching keywords and making modifications...")
    if len(keyword_shortlist) == 0:
        print("No keywords shortlisted!")
        exit()

    required_pos = {"head", "join", "tail", "suff", "pref"}
    for keyword_obj in keyword_shortlist:
        pos = keyword_obj.pos
        if pos in pos_conversion.keys():
            pos = pos_conversion[pos]
        required_pos.add(pos)
        modifier_list = required_comps[pos]
        for kw_modifier in modifier_list:
            key = f"{pos}|{kw_modifier}"
            modword_list = keyword_modifier(keyword_obj, kw_modifier)
            for modword_obj in modword_list:
                keyword_dict[key].add(modword_obj)

        # Generate plural:
        if pos == "noun":
            pos = "plrn"
            required_pos.add(pos)
            plural_noun_str = pluralize(keyword_obj.keyword)
            keyword_obj: Keyword = copy.deepcopy(keyword_obj)
            keyword_obj.keyword = plural_noun_str
            keyword_obj.pos = "plural_noun"
            keyword_obj.phonetic_grade, keyword_obj.phonetic_pattern = grade_phonetic(plural_noun_str)
            modifier_list = required_comps[pos]
            for kw_modifier in modifier_list:
                key = f"{pos}|{kw_modifier}"
                modword_list = keyword_modifier(keyword_obj, kw_modifier)
                for modword_obj in modword_list:
                    keyword_dict[key].add(modword_obj)

    algorithms = set()
    for algorithm in raw_algorithms:
        status = "used"
        for component in algorithm.components:
            if component.pos not in required_pos:
                status = "not_used"
        if status == "used":
            algorithms.add(algorithm)
        else:
            print(f"Algorithm '{algorithm}' removed!")

    # Pull required dictionaries
    print("Pulling required dictionaries...")
    if "pref" in required_comps.keys():
        pos = "prefix"
        sheet_name = "prefixes"
        prefix_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name)   
        keyword_dict["pref|no_cut"] = set(pull_dictionary(prefix_file, pos))

    if "suff" in required_comps.keys():
        pos = "suffix"
        sheet_name = "suffixes"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name)  
        keyword_dict["suff|no_cut"] = set(pull_dictionary(json_file, pos))

    if "head" in required_comps.keys():
        pos = "head"
        sheet_name = "heads"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name)  
        keyword_dict["head|no_cut"] = set(pull_dictionary(json_file, pos))

    if "tail" in required_comps.keys():
        pos = "tail"
        sheet_name = "tails"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name)  
        keyword_dict["tail|no_cut"] = set(pull_dictionary(json_file, pos))

    if "join" in required_comps.keys():
        pos = "join"
        sheet_name = "joints"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name)  
        keyword_dict["join|no_cut"] = set(pull_dictionary(json_file, pos))

    keyword_dict_json = {}
    for key, item in keyword_dict.items():
        keyword_dict_json[key] = list(item)
    with open(keyword_dict_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict_json, option=json.OPT_INDENT_2))
    
    print("Generating keywords shortlist...")  
    shortlisted_keyword_dict = []
    required = ["noun", "plrn", "verb", "adje", "advb"]
    for key in keyword_dict_json.keys():
        if key[:4] in required:
            for keyword_obj in keyword_dict_json[key]:
                keyword_obj = dataclasses.asdict(keyword_obj)
                desired_order_list = [
                    "origin",
                    "source_word",
                    "spacy_pos",
                    "wordsAPI_pos",
                    "keyword_len",
                    "contained_words",
                    "phonetic_grade",
                    "yake_rank",
                    "modifier",
                    "modword_len",
                    "pos",
                    "keyword",
                    "modword",
                    "shortlist",
                ]
                reordered_keyword_dict = {key: keyword_obj[key] for key in desired_order_list}
                shortlisted_keyword_dict.append(reordered_keyword_dict)
    keyword_dict_sorted = sorted(shortlisted_keyword_dict, key=lambda d: [d['keyword'], d['pos'], d['modifier']])

    # Pull wordsAPI data
    wordsapi_data = pull_wordsAPI_dict()
    wiki_titles_data = set(open(wiki_titles_data_fp, "r").read().splitlines())

    # Removing previously generated names and domains 
    if os.path.exists(remaining_shortlist_json_fp):
        os.remove(remaining_shortlist_json_fp)
    if os.path.exists(previous_domain_output_fp):
        os.remove(previous_domain_output_fp)

    # Generate names
    all_names = make_names(algorithms, keyword_dict, wordsapi_data)
    print("Exporting ungraded_names.json to tmp folder...")
    with open(json_ungraded_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Generating names shortlist...")  
    graded_names = {}
    name: Name
    for name in all_names.values():
        etymology_data: Etymology
        for etymology_data in name.etymologies:
            name_in_lower_str = name.name_in_lower
            name_in_title_str = etymology_data.name_in_title
            name_type_str = etymology_data.name_type
            keyword_combination = "".join(etymology_data.keyword_tuple)
            pos_combination = "+".join(etymology_data.pos_tuple)
            modifier_combination = "+".join(etymology_data.modifier_tuple)
            etymology_repr = repr(etymology_data)
            key = f"{name_in_title_str}({name_type_str})"
            wiki_title_check = check_if_wiki_title(name.is_word, name_in_lower_str, wiki_titles_data)

            if not key in graded_names.keys():

                keywords_list = sorted(set(etymology_data.keyword_tuple))
                contained_words_list = find_contained_words(name_in_title_str, wordsapi_data, keywords_list)
                grade_str = grade_name(name_type_str, name.phonetic_grade, name.non_plaus_letter_combs, name.is_word, name.length, contained_words_list, wiki_title_check)

                graded_names[key] = Graded_name(
                    name_in_lower = name_in_lower_str,
                    name_in_title = name_in_title_str,
                    name_type = name_type_str,
                    length = name.length,
                    phonetic_grade = name.phonetic_grade,
                    non_plaus_letter_combs = name.non_plaus_letter_combs,
                    is_word = name.is_word,
                    contained_words = contained_words_list,
                    wiki_title = wiki_title_check,
                    keywords = keywords_list,
                    keyword_combinations = [keyword_combination],
                    pos_combinations = [pos_combination],
                    modifier_combinations = [modifier_combination],
                    etymologies = [etymology_repr],
                    grade = grade_str,
                )

            else:
                data:Graded_name = copy.deepcopy(graded_names[key])
                keywords_list = sorted(set(data.keywords + list(etymology_data.keyword_tuple)))
                contained_words_list = find_contained_words(name_in_title_str, wordsapi_data, keywords_list)
                grade_str = grade_name(name_type_str, name.phonetic_grade, name.non_plaus_letter_combs, name.is_word, name.length, contained_words_list, wiki_title_check)
                data.contained_words = contained_words_list
                data.keywords = keywords_list
                data.keyword_combinations = sorted(set(data.keyword_combinations + [keyword_combination]))
                data.pos_combinations = sorted(set(data.pos_combinations + [pos_combination]))
                data.modifier_combinations = sorted(set(data.modifier_combinations + [modifier_combination]))
                data.etymologies = sorted(set(data.etymologies + [repr(etymology_data)]))
                data.grade = grade_str
                graded_names[key] = data

    # Sort graded names according to grade.
    sorted_graded_names_list = sorted(graded_names, key=lambda k: (str(graded_names[k].grade or "ZZZZZ"), graded_names[k].length, graded_names[k].name_in_lower))
    sorted_graded_names = {}
    for name in sorted_graded_names_list:
        sorted_graded_names[name] = graded_names[name]

    print("Exporting graded names.json...")
    with open(json_graded_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(sorted_graded_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Preparing data for export...")
    cut_name = []
    text_comp_name = []
    no_cut_name = []
    pref_suff_name = []
    shortlisted_names = {}
    shortlisted_names["cut_name"] = {}
    shortlisted_names["text_comp_name"] = {}
    shortlisted_names["pref_suff_name"] = {}
    shortlisted_names["no_cut_name"] = {}

    name_types = ["cut_name", "cn_percentage", "text_comp_name", "tcn_percentage", "pref_suff_name", "psn_percentage", "no_cut_name", "ncn_percentage"]
    raw_statistics = {}
    for name_type in name_types:
        raw_statistics[name_type] = {}
    for key, data in sorted_graded_names.items():
        name_in_title = data.name_in_title
        grade = data.grade if data.grade is not None else "Discarded"
        name_type = data.name_type
        raw_statistics[name_type][grade] = raw_statistics[name_type].get(grade, 0) + 1
        raw_statistics[name_type]["Total"] = raw_statistics[name_type].get("Total", 0) + 1
        if grade != "Discarded":
            raw_statistics[name_type]["Graded"] = raw_statistics[name_type].get("Graded", 0) + 1
            shortlisted_names[name_type][name_in_title] = data
        if name_type == "cut_name":
            cut_name.append(data)
        elif name_type == "text_comp_name":
            text_comp_name.append(data)
        elif name_type == "pref_suff_name":
            pref_suff_name.append(data)
        elif name_type == "no_cut_name":
            no_cut_name.append(data)

    print("Exporting shortlisted_names.json...")
    with open(json_sl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(shortlisted_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Exporting raw_stats.json...")
    try:
        with open(json_stats_output_fp, "wb+") as out_file:
            out_file.write(json.dumps(raw_statistics, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))
    except TypeError:
        pass


    print("Exporting names.xlsx...")
    # Excel output for prototype only: for production, remove code below
    cut_names_len = len(cut_name)
    pref_suff_names_len = len(pref_suff_name)
    text_comp_names_len = len(text_comp_name)
    no_cut_names_len = len(no_cut_name)
    grades = ["Grade_A", "Grade_B", "Grade_C", "Grade_D", "Graded", "Discarded", "Total"]
    statistics = {}
    for index, name_type in enumerate(name_types):
        statistics[name_type] = {}
        for grade in grades:
            try:
                statistics[name_type][grade] = raw_statistics[name_type][grade]
            except KeyError:
                try:
                    statistics[name_type][grade] = str(round(raw_statistics[name_types[index-1]][grade]/raw_statistics[name_types[index-1]]["Total"]*100,2)) + "%"
                except KeyError:
                    if name_type in ["cn_percentage", "tcn_percentage", "ncn_percentage", "psn_percentage"]:
                        statistics[name_type][grade] = "0%"
                    else:
                        statistics[name_type][grade] = 0

    df1 = pd.DataFrame.from_dict(keyword_dict_sorted, orient="columns")
    df2 = pd.DataFrame.from_dict(cut_name, orient="columns")
    df3 = pd.DataFrame.from_dict(pref_suff_name, orient="columns")
    df4 = pd.DataFrame.from_dict(text_comp_name, orient="columns")
    df5 = pd.DataFrame.from_dict(no_cut_name, orient="columns")
    df6 = pd.DataFrame.from_dict(statistics)

    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')
    df1.to_excel(writer, sheet_name=f'shortlisted keywords')
    df2.to_excel(writer, sheet_name=f'cut names ({cut_names_len})')
    df3.to_excel(writer, sheet_name=f'pref suff names ({pref_suff_names_len})')
    df4.to_excel(writer, sheet_name=f'text comp names ({text_comp_names_len})')
    df5.to_excel(writer, sheet_name=f'no cut names ({no_cut_names_len})')
    df6.to_excel(writer, sheet_name=f'statistics')
    workbook  = writer.book
    worksheet = writer.sheets['shortlisted keywords']
    worksheet.set_column(1, 14, 15)
    worksheet = writer.sheets[f'cut names ({cut_names_len})']
    worksheet.set_column(1, 15, 15)
    worksheet = writer.sheets[f'pref suff names ({pref_suff_names_len})']
    worksheet.set_column(1, 15, 15)
    worksheet = writer.sheets[f'text comp names ({text_comp_names_len})']
    worksheet.set_column(1, 15, 15)
    worksheet = writer.sheets[f'no cut names ({no_cut_names_len})']
    worksheet.set_column(1, 15, 15)
    worksheet = writer.sheets['statistics']
    worksheet.set_column(1, 8, 15)
    writer.save()

if __name__ == "__main__":
    generate_names(sys.argv[1])
