#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
import os
import copy
import pandas as pd
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
from modules.pull_eng_dict import pull_eng_dict
from modules.process_user_keywords import process_user_keywords_dict
from modules.verify_words_with_eng_dict import verify_words_with_eng_dict
from modules.pull_user_keyword_bank import pull_user_keyword_bank
from modules.keyword_modifier import keyword_modifier
from modules.grade_phonetic import grade_phonetic
from modules.grade_name import grade_name
from modules.manage_contained_words import pull_master_exempt, push_contained_words_list


def process_additional_keywords(additional_keyword_list_fp, project_path, master_exempt_contained_words):
    keywords_json_fp = f"{project_path}/tmp/name_generator/additional_keywords.json"
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

def check_if_wiki_title(is_word, name_in_lower: str, wiki_titles_list: list[str]):
    if name_in_lower in wiki_titles_list:
        value = f"yes: {name_in_lower}"
    else:
        value = None
    return value

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
                    restrictions_before=data["restrictions_before"],
                    restrictions_after=data["restrictions_after"],
                    restrictions_as_joint=data["restrictions_as_joint"],
                    keyword_class="standard",
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
    curated_eng_list_fp = "name_generator/curated_eng_word_list.txt"

    # tmp file filepaths and filenames:
    required_comps_tsv_fp = f"{project_path}/tmp/name_generator/{project_id}_comps.tsv"
    keyword_dict_json_fp = f"{project_path}/tmp/name_generator/{project_id}_keyword_dict.json"
    json_ungraded_output_fp = f"{project_path}/tmp/name_generator/{project_id}_ungraded_names.json"
    json_graded_output_fp = f"{project_path}/tmp/name_generator/{project_id}_graded_names.json"
    remaining_shortlist_json_fp = f"{project_path}/tmp/name_generator/{project_id}_remaining_shortlist.json"
    json_sl_output_fp = f"{project_path}/tmp/name_generator/{project_id}_names_shortlist.json"
    json_kc_output_fp = f"{project_path}/tmp/name_generator/{project_id}_keyword_combos.json"
    json_stats_output_fp = f"{project_path}/tmp/name_generator/{project_id}_names_statistics.json"
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp = f"{project_path}/results/{project_id}_names.xlsx"

    # Pull eng_dict data
    eng_dict_data: dict = pull_eng_dict()
    eng_dict_words: set = set(list(eng_dict_data.keys()))
    wiki_titles_data: set = set(open(wiki_titles_data_fp, "r").read().splitlines())
    curated_eng_list = set(open(curated_eng_list_fp, "r").read().splitlines())

    # Pull master exempt contained words list
    master_exempt_contained_words = pull_master_exempt()

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
    keywords_json_mfp = convert_excel_to_json(keyword_fp, target_sheets=sheets, output_json_fp=keywords_json_fp, convert_list=True)
    with open(keywords_json_mfp) as keyword_file:
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
            if modword_list is not None:
                for modword_obj in modword_list:
                    keyword_dict[key].add(modword_obj)

        # Generate plural:
        if pos == "noun":
            plural_noun_str = pluralize(keyword_obj.keyword)
            if plural_noun_str[-2:] != "ss":
                pos = "plrn"
                required_pos.add(pos)
                keyword_obj: Keyword = copy.deepcopy(keyword_obj)
                keyword_obj.keyword = plural_noun_str
                keyword_obj.pos = "plural_noun"
                keyword_obj.phonetic_grade, keyword_obj.phonetic_pattern = grade_phonetic(plural_noun_str)
                keyword_obj.contained_words = find_contained_words(keyword=plural_noun_str, curated_eng_list=curated_eng_list, type="keyword", exempt=master_exempt_contained_words)
                keyword_obj.keyword_class = "prime"
                modifier_list = required_comps[pos]
                for kw_modifier in modifier_list:
                    key = f"{pos}|{kw_modifier}"
                    modword_list = keyword_modifier(keyword_obj, kw_modifier)
                    if modword_list is not None:
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
        prefix_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name, convert_list=True)   
        keyword_dict["pref|no_cut"] = set(pull_dictionary(prefix_file, pos))

    if "suff" in required_comps.keys():
        pos = "suffix"
        sheet_name = "suffixes"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name, convert_list=True)  
        keyword_dict["suff|no_cut"] = set(pull_dictionary(json_file, pos))

    if "head" in required_comps.keys():
        pos = "head"
        sheet_name = "heads"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name, convert_list=True)  
        keyword_dict["head|no_cut"] = set(pull_dictionary(json_file, pos))

    if "tail" in required_comps.keys():
        pos = "tail"
        sheet_name = "tails"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name, convert_list=True)  
        keyword_dict["tail|no_cut"] = set(pull_dictionary(json_file, pos))

    if "join" in required_comps.keys():
        pos = "join"
        sheet_name = "joints"
        json_file = convert_excel_to_json(text_components_data_xlsx_fp, sheet_name, convert_list=True)  
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
                    "shortlist",
                ]
                reordered_keyword_dict = {key: keyword_obj[key] for key in desired_order_list}
                shortlisted_keyword_dict.append(reordered_keyword_dict)
    keyword_dict_sorted = sorted(shortlisted_keyword_dict, key=lambda d: [d['keyword'], d['pos'], d['modifier']])

    # Removing previously generated names and domains 
    if os.path.exists(remaining_shortlist_json_fp):
        os.remove(remaining_shortlist_json_fp)
    if os.path.exists(previous_domain_output_fp):
        os.remove(previous_domain_output_fp)

    # Generate names
    all_names = make_names(algorithms, keyword_dict, eng_dict_words)
    print("Exporting ungraded_names.json to tmp folder...")
    with open(json_ungraded_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print("Generating names shortlist...")  
    graded_names = {}
    name: Name
    for name in all_names.values():
        etymology_data: Etymology
        exempt_contained_list = []
        for etymology_data in name.etymologies:
            name_in_lower_str = name.name_in_lower
            name_in_title_str = etymology_data.name_in_title
            name_type_str = etymology_data.name_type
            keyword_combination = "|".join([x.title() for x in etymology_data.keyword_tuple])
            pos_combination = "+".join(etymology_data.pos_tuple)
            modifier_combination = "+".join(etymology_data.modifier_tuple)
            etymology_repr = repr(etymology_data)
            key = f"{name_in_title_str}({name_type_str})"
            wiki_title_check = check_if_wiki_title(name.is_word, name_in_lower_str, wiki_titles_data)

            if key not in graded_names.keys():
                modwords_list = sorted(set(etymology_data.modword_tuple))
                keywords_list = sorted(set(etymology_data.keyword_tuple))
                exempt_contained_list = sorted(set(list(name.exempt_contained) + list(exempt_contained_list))) if name.exempt_contained else list(exempt_contained_list)
                contained_words_list = find_contained_words(keyword=name_in_title_str, curated_eng_list=curated_eng_list, type="name", exempt=exempt_contained_list)
                grade_str, reject_reason = grade_name(name_type_str, name.phonetic_grade, name.implaus_chars, name.end_valid, name.is_word, name.length, contained_words_list, wiki_title_check)
                if name.keyword_classes == ['prime']:
                    name_class_str = "Class_1"
                elif name.keyword_classes == ['prime', 'standard']:
                    name_class_str = "Class_2"
                else:
                    name_class_str = "Class_3"

                graded_names[key] = Graded_name(
                    name_in_lower = name_in_lower_str,
                    name_in_title = name_in_title_str,
                    name_type = name_type_str,
                    length = name.length,
                    phonetic_pattern= name.phonetic_pattern,
                    phonetic_grade = name.phonetic_grade,
                    implaus_chars = name.implaus_chars,
                    end_valid = name.end_valid,
                    is_word = name.is_word,
                    exempt_contained = exempt_contained_list,
                    contained_words = list(contained_words_list) if contained_words_list else None,
                    wiki_title = wiki_title_check,
                    modwords = modwords_list,
                    keywords = keywords_list,
                    keyword_combinations = [keyword_combination],
                    pos_combinations = [pos_combination],
                    keyword_pos_combos={keyword_combination:[pos_combination]},
                    modifier_combinations = [modifier_combination],
                    keyword_classes = name.keyword_classes,
                    etymologies = [etymology_repr],
                    etymology_count = 1,
                    grade = grade_str,
                    name_class=name_class_str,
                    reject_reason = reject_reason
                )

            else:
                data:Graded_name = copy.deepcopy(graded_names[key])
                modwords_list = sorted(set(list(data.modwords) + list(etymology_data.modword_tuple)))
                keywords_list = sorted(set(list(data.keywords) + list(etymology_data.keyword_tuple)))
                exempt_contained_list = sorted(set(list(data.exempt_contained) + list(name.exempt_contained) + list(exempt_contained_list))) if name.exempt_contained else sorted(set(list(data.exempt_contained) + list(exempt_contained_list)))
                contained_words_list = find_contained_words(keyword=name_in_title_str, curated_eng_list=curated_eng_list, type="name", exempt=exempt_contained_list)
                grade_str, reject_reason = grade_name(name_type_str, name.phonetic_grade, name.implaus_chars, name.end_valid, name.is_word, name.length, contained_words_list, wiki_title_check)

                contained_words = []
                if data.contained_words is not None:
                    contained_words = contained_words + data.contained_words
                if contained_words_list is not None:
                    contained_words = contained_words + contained_words_list
                if len(contained_words) > 0:
                    contained_words = sorted(set(contained_words))
                else:
                    contained_words = None

                keyword_class_list = sorted(set(data.keyword_classes + name.keyword_classes))
                if keyword_class_list == ['prime']:
                    name_class_str = "Class_1"
                elif keyword_class_list == ['prime', 'standard']:
                    name_class_str = "Class_2"
                else:
                    name_class_str = "Class_3"

                keyword_pos_combos = data.keyword_pos_combos
                if keyword_combination in keyword_pos_combos.keys():
                    keyword_pos_combos[keyword_combination].append(pos_combination)
                else:
                    keyword_pos_combos[keyword_combination] = [pos_combination]

                data.contained_words = contained_words_list
                data.keywords = keywords_list
                data.keyword_combinations = sorted(set(data.keyword_combinations + [keyword_combination]))
                data.pos_combinations = sorted(set(data.pos_combinations + [pos_combination]))
                data.keyword_pos_combos = keyword_pos_combos
                data.modifier_combinations = sorted(set(data.modifier_combinations + [modifier_combination]))
                data.keyword_classes = keyword_class_list
                data.etymologies = sorted(set(data.etymologies + [repr(etymology_data)]))
                data.etymology_count = len(data.etymologies)
                data.exempt_contained = exempt_contained_list
                data.contained_words = contained_words
                data.grade = grade_str
                data.name_class = name_class_str
                data.reject_reason = reject_reason
                graded_names[key] = data

    # Sort graded names according to grade.
    sorted_graded_names_list = sorted(graded_names, key=lambda k: (graded_names[k].length, str(graded_names[k].grade or "ZZZZZ"), graded_names[k].name_class, graded_names[k].name_in_lower))
    sorted_graded_names = {}
    for name in sorted_graded_names_list:
        sorted_graded_names[name] = graded_names[name]
    print("Exporting graded names.json...")
    with open(json_graded_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(sorted_graded_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    # Update and export contained words list
    push_contained_words_list(sorted_graded_names, master_exempt_contained_words)

    print("Preparing data for export...")
    name_types = ["repeating_name", "rpn_percentage", "fit_name", "fn_percentage", "text_comp_name", "tcn_percentage", "pref_suff_name", "psn_percentage", "cut_name", "cn_percentage", "part_cut_name", "pcn_percentage", "no_cut_name", "ncn_percentage"]
    keyword_combos = {}
    keyword_combo_set = set()
    sorted_names = {"keyword_combinations": [], "shortlisted keywords": keyword_dict_sorted}
    raw_statistics = {}
    for name_type in name_types:
        raw_statistics[name_type] = {}
        if not name_type.endswith("percentage"):
            sorted_names[name_type] = {}
    for key, data in sorted_graded_names.items():
        name_in_title_str = data.name_in_title
        grade = data.grade if data.grade is not None else "Discarded"
        if data.name_type[:4] == "fit_":
            name_type = "fit_name"
        elif data.name_type[:10] == "repeating_":
            name_type = "repeating_name"
        else:
            name_type = data.name_type
        raw_statistics[name_type][grade] = raw_statistics[name_type].get(grade, 0) + 1
        raw_statistics[name_type]["Total"] = raw_statistics[name_type].get("Total", 0) + 1
        for keyword_combination in data.keyword_combinations:
            pos_combinations = data.keyword_pos_combos[keyword_combination]
            if grade != "Discarded":
                raw_statistics[name_type]["Graded"] = raw_statistics[name_type].get("Graded", 0) + 1
                if keyword_combination not in keyword_combo_set:
                    keyword_combos[keyword_combination] = {}
                    keyword_combos[keyword_combination]["pos_combinations"] = pos_combinations
                    keyword_combos[keyword_combination]["combination_count"] = 1
                    keyword_combos[keyword_combination]["name_count"] = 1
                    keyword_combos[keyword_combination]["names_list"] = [name_in_title_str]
                    keyword_combos[keyword_combination]["names"] = [data]
                    keyword_combo_set.add(keyword_combination)
                else:
                    pos_combinations = list(set(keyword_combos[keyword_combination]["pos_combinations"] + pos_combinations))
                    names_list = list(set(keyword_combos[keyword_combination]["names_list"] + [name_in_title_str]))
                    keyword_combos[keyword_combination]["pos_combinations"] = pos_combinations
                    keyword_combos[keyword_combination]["combination_count"] = len(pos_combinations)
                    keyword_combos[keyword_combination]["name_count"] = len(keyword_combos[keyword_combination]["names"])
                    keyword_combos[keyword_combination]["names_list"] = names_list
                    keyword_combos[keyword_combination]["names"].append(data)
            sorted_names[name_type][name_in_title_str] = data

    print("Exporting keyword_combos.json...")
    with open(json_kc_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(keyword_combos, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print(f"Exporting {project_id}_names_statistics.json...")
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
                    if name_type in ["rpn_percentage", "fn_percentage", "tcn_percentage", "psn_percentage", "cn_percentage", "pcn_percentage", "ncn_percentage"]:
                        statistics[name_type][grade] = "0%"
                    else:
                        statistics[name_type][grade] = 0
    try:
        with open(json_stats_output_fp, "wb+") as out_file:
            out_file.write(json.dumps(statistics, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))
    except TypeError:
        print("raw_statistics encountered TypeError!")
        with open(json_stats_output_fp, 'r') as file:
            file.write(str(statistics).encode())

    print(f"Preparing {project_id}_names.xlsx...")
    sorted_keyword_combination = sorted(keyword_combo_set)
    keyword_combination_list = []
    for keyword_combination in sorted_keyword_combination:
        data = keyword_combos[keyword_combination]
        keyword_combination_str = keyword_combination.replace("|", "")
        kc_list = keyword_combination.split("|")
        kc_list_len = len(kc_list)
        keyword_1 = None
        keyword_2 = None
        keyword_3 = None
        if kc_list_len == 1:
            keyword_1 = kc_list[0]
        elif kc_list_len == 2:
            keyword_1 = kc_list[0]
            keyword_2 = kc_list[1]
        elif kc_list_len == 3:
            keyword_1 = kc_list[0]
            keyword_2 = kc_list[1]
            keyword_3 = kc_list[2]
        data["keyword_list"] = kc_list
        data["keyword_1"] = keyword_1
        data["keyword_2"] = keyword_2
        data["keyword_3"] = keyword_3
        data["keyword_combination"] = keyword_combination_str
        data["remove"] = None
        del data["names"]
        keyword_combination_list.append(data)

    sorted_keyword_combination_list = sorted(keyword_combination_list, key=lambda d: (-d["name_count"], d["keyword_combination"]))
    sorted_names["keyword_combinations"] = sorted_keyword_combination_list
    sorted_names["statistics"] = statistics

    print("Exporting name_shortlist.json...")
    with open(json_sl_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(sorted_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    print(f"Exporting {project_id}_names.xlsx...")
    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')
    sheet_names = []
    for name_type, data in sorted_names.items():
        if type(data) == dict:
            data = list(data.values())
        df = pd.DataFrame.from_dict(data, orient="columns")
        list_len = len(data)
        if name_type != 'statistics':
            sheet_name_str = f"{name_type} ({list_len})"
        else:
            sheet_name_str = name_type
        sheet_names.append(sheet_name_str)
        df.to_excel(writer, sheet_name=sheet_name_str)
    
    workbook  = writer.book
    for sheet_name in sheet_names:
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column(1, 15, 15)
    writer.save()

if __name__ == "__main__":
    generate_names(sys.argv[1])
