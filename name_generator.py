#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
import os
import copy
from typing import List
from pattern3.text.en import pluralize
from classes.keyword_class import Keyword
from classes.name_class import Etymology, Name
from classes.name_class import Graded_name
from modules.make_names import make_names
from modules.collect_algorithms import collect_algorithms
from modules.convert_excel_to_json import convert_excel_to_json
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.find_contained_words import find_contained_words
from modules.pull_wordsAPI import pull_wordsAPI_dict

# Pandas input/output for prototype only: remove for production
import pandas as pd

def grade_name(name_type, phonetic_grade, word_plaus, is_it_word, name_length, contained_words, if_wiki_title):

    grade_str = None

    if name_type == "cut_name":
        if (
            word_plaus == "yes" 
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
            is_it_word == "no"
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

    target_list = []
    for data in dictionary_data:
        if data["shortlist"] is not None and data["shortlist"] != "":
            target_list.append(
                Keyword(
                    origin="dictionary",
                    keyword=data["keyword"],
                    keyword_len=data["keyword_len"],
                    pos=pos_str,
                    restrictions_before=isNone(data["restrictions_before"].replace(",","").split()),
                    restrictions_after=isNone(data["restrictions_after"].replace(",","").split()),
                    restrictions_as_joint=isNone(data["restrictions_as_joint"].replace(",","").split()),
                    shortlist=data["shortlist"]
                )
        )
    return target_list

# Generate name ideas
# "keyword_fp", "algorithm_fp", "json_output_fp", "xlsx_output_fp" inputs are filepaths
def generate_names(keyword_fp: str, algorithm_fp: str, json_output_fp: str):

    # Convert algorithm excel file to json file (remove when excel files not used anymore)
    sheet_name = "algorithms"
    algorithm_fp = convert_excel_to_json(algorithm_fp, target_sheet=sheet_name)

    # Get all algorithms
    print("Loading algorithms...")
    algorithms = collect_algorithms(algorithm_fp)
    comp_list_types = []
    required_comps = []

    for algorithm in algorithms:
        comp_list_type = sorted([component.pos for component in algorithm.components])
        if comp_list_type not in comp_list_types:
            comp_list_types.append(comp_list_type)

    # Get all elements used in comp_list
    for comp_list_type in comp_list_types:
        for comp in comp_list_type:
            if comp not in required_comps:
                required_comps.append(comp)

    # Access keyword list and sort words into verbs, nouns or adjectives
    # Excel input for prototype only: for production, import directly from json

    sheets = ["nouns", "verbs", "adjectives", "adverbs"]
    old_data_fp = convert_excel_to_json(keyword_fp, target_sheets=sheets)
    with open(old_data_fp) as keyword_file:
        keyword_data = json.loads(keyword_file.read())
    keyword_shortlist = generate_keyword_shortlist(keyword_data)

    verbs = []
    nouns = []
    plural_nouns = []
    adjectives = []
    adverbs = []

    print("Fetching keywords...")
    if len(keyword_shortlist) == 0:
        print("No keywords shortlisted!")
        exit()

    for keyword_obj in keyword_shortlist:

        if keyword_obj.pos == "noun":
            nouns.append(keyword_obj)

            # Generate plural:
            plural_noun_str = pluralize(keyword_obj.keyword)
            keyword_obj: Keyword = copy.deepcopy(keyword_obj)
            keyword_obj.keyword = plural_noun_str
            plural_nouns.append(keyword_obj)

        elif keyword_obj.pos == "verb":
            verbs.append(keyword_obj)
        elif keyword_obj.pos == "adjective":
            adjectives.append(keyword_obj)
        elif keyword_obj.pos == "adverb":
            adverbs.append(keyword_obj)

    # Pull required dictionaries
    print("Pulling required dictionaries...")
    if "pref" in required_comps:
        prefix_fp = "dict/text_components.xlsx"
        pos = "prefix"
        sheet_name = "prefixes"
        prefix_file = convert_excel_to_json(prefix_fp, sheet_name)   
        prefixes = pull_dictionary(prefix_file, pos)
    else:
        prefixes = []

    if "suff" in required_comps:
        data_fp = "dict/text_components.xlsx"
        pos = "suffix"
        sheet_name = "suffixes"
        json_file = convert_excel_to_json(data_fp, sheet_name)  
        suffixes = pull_dictionary(json_file, pos)
    else:
        suffixes = []

    if "head" in required_comps:
        data_fp = "dict/text_components.xlsx"
        pos = "head"
        sheet_name = "heads"
        json_file = convert_excel_to_json(data_fp, sheet_name)  
        heads = pull_dictionary(json_file, pos)
    else:
        heads = []

    if "tail" in required_comps:
        data_fp = "dict/text_components.xlsx"
        pos = "tail"
        sheet_name = "tails"
        json_file = convert_excel_to_json(data_fp, sheet_name)  
        tails = pull_dictionary(json_file, pos)
    else:
        tails = []

    if "join" in required_comps:
        data_fp = "dict/text_components.xlsx"
        pos = "join"
        sheet_name = "joints"
        json_file = convert_excel_to_json(data_fp, sheet_name)  
        joints = pull_dictionary(json_file, pos)
    else:
        joints = []

    # Add all lists into dict form
    keyword_dict = {
        "verb": verbs,
        "noun": nouns,
        "plrn": plural_nouns,
        "adje": adjectives,
        "advb": adverbs,
        "pref": prefixes,
        "suff": suffixes,
        "head": heads,
        "join": joints,
        "tail": tails,
    }
    with open("tmp/keyword_generator/keyword_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict, option=json.OPT_INDENT_2))
    
    # Pull wordsAPI data
    wordsapi_data = pull_wordsAPI_dict()
    wiki_titles_data = set(open("../wikipedia_extract_titles/results/wiki_titles_combined_list_filtered.tsv", "r").read().splitlines())

    # Generate names
    all_names = make_names(algorithms, keyword_dict, wordsapi_data)
    print("Exporting ungraded_names.json to tmp folder...")
    json_ungraded_output_fp = json_output_fp.replace("results/", f"tmp/name_generator/ungraded_")
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
                grade_str = grade_name(name_type_str, name.phonetic_grade, name.word_plausibility, name.is_word, name.length, contained_words_list, wiki_title_check)

                graded_names[key] = Graded_name(
                    name_in_lower = name_in_lower_str,
                    name_in_title = name_in_title_str,
                    name_type = name_type_str,
                    length = name.length,
                    phonetic_grade = name.phonetic_grade,
                    word_plausibility = name.word_plausibility,
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
                grade_str = grade_name(name_type_str, name.phonetic_grade, name.word_plausibility, name.is_word, name.length, contained_words_list, wiki_title_check)
                data.contained_words = contained_words_list
                data.keywords = keywords_list
                data.keyword_combinations = sorted(set(data.keyword_combinations + [keyword_combination]))
                data.pos_combinations = sorted(set(data.pos_combinations + [pos_combination]))
                data.modifier_combinations = sorted(set(data.modifier_combinations + [modifier_combination]))
                data.etymologies = sorted(set(data.etymologies + [repr(etymology_data)]))
                data.grade = grade_str
                graded_names[key] = data

    # Removing previously generated names and domains 
    tmp_file="tmp/name_generator/remaining_shortlist.json"
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    previous_domain_output_fp = "results/domains.json"
    if os.path.exists(previous_domain_output_fp):
        os.remove(previous_domain_output_fp)

    print("Exporting names.json...")
    json_graded_output_fp = json_output_fp.replace("results/", f"tmp/name_generator/graded_")
    with open(json_graded_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(graded_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Preparing data for export...")
    cut_name = []
    text_comp_name = []
    no_cut_name = []
    shortlisted_names = {}
    shortlisted_names["cut_name"] = {}
    shortlisted_names["text_comp_name"] = {}
    shortlisted_names["no_cut_name"] = {}

    name_types = ["cut_name", "cn_percentage", "text_comp_name", "tcn_percentage", "no_cut_name", "ncn_percentage"]
    raw_statistics = {}
    for name_type in name_types:
        raw_statistics[name_type] = {}

    for key, data in graded_names.items():
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
        elif name_type == "no_cut_name":
            no_cut_name.append(data)

    print("Exporting shortlisted_names.json...")
    json_sl_output_fp = json_output_fp.replace(".json", f"_shortlist.json").replace("results/", f"tmp/name_generator/")
    with open(json_sl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(shortlisted_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Exporting names.xlsx...")
    # Excel output for prototype only: for production, remove code below
    cut_names_len = len(cut_name)
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
                statistics[name_type][grade] = str(round(raw_statistics[name_types[index-1]][grade]/raw_statistics[name_types[index-1]]["Total"]*100,2)) + "%"

    df1 = pd.DataFrame.from_dict(cut_name, orient="columns")
    df2 = pd.DataFrame.from_dict(text_comp_name, orient="columns")
    df3 = pd.DataFrame.from_dict(no_cut_name, orient="columns")
    df4 = pd.DataFrame.from_dict(statistics)
    excel_output_fp = json_output_fp.replace(".json", ".xlsx")
    writer = pd.ExcelWriter(excel_output_fp)
    df1.to_excel(writer, sheet_name=f'cut names ({cut_names_len})')
    df2.to_excel(writer, sheet_name=f'text comp names ({text_comp_names_len})')
    df3.to_excel(writer, sheet_name=f'no cut names ({no_cut_names_len})')
    df4.to_excel(writer, sheet_name=f'statistics')
    writer.save()

if __name__ == "__main__":
    generate_names(sys.argv[1], sys.argv[2], sys.argv[3])
