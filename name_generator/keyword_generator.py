#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword
from classes.keyword_class import Preferred_Keyword
import sys
import orjson as json
from typing import List, Dict
import copy
import os.path
from modules.process_text_with_spacy import process_text_with_spacy
from modules.verify_words_with_eng_dict import verify_words_with_eng_dict
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.convert_excel_to_json import convert_excel_to_json
from modules.filter_keywords import filter_keywords
from modules.yake_keyword_extractor import keyword_extractor
from modules.run_googletrans import get_translation
from modules.process_user_keywords import process_user_keywords_str
from modules.pull_user_keyword_bank import pull_user_keyword_bank
from modules.manage_contained_words import pull_master_exempt, push_contained_words_list

# Pandas input/output for prototype only: remove for production
import pandas as pd

# "text_file" input is a filepath
# "user_keywords_file" input is a filepath
# "output" input is a filepath
def generate_word_list(project_id):

    project_path: str = f"projects/{project_id}"

    # input file filepaths and filenames:
    keyword_list_tsv_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_user_keywords.tsv"
    sentences_tsv_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_user_sentences.tsv"

    # tmp file filepaths and filenames:
    keyword_list_keywords_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_keywords_from_keyword-list.json"
    sentences_keywords_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_keywords_from_sentences.json"
    rated_kw_tmp_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_all_keywords.json"
    yake_tmp_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_yake_keywords.json"
    gootrans_tmp_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_google_trans.json"
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp: str = f"{project_path}/results/{project_id}_keywords.xlsx"

    # Set variable defaults
    all_keywords: List[Keyword] = []
    all_keywords_dict: Dict[str, Dict[str, Keyword]] = {}
    keyword_list = None
    sentences = None

    # Pull master exempt contained words list
    master_exempt_contained_words = pull_master_exempt()

    # Check if keywords exists and create keywords from keywords list
    if os.path.exists(keyword_list_tsv_fp):
        keyword_list = [s for s in open(keyword_list_tsv_fp, "r").read().replace(" ", "\n").splitlines() if s]
        if len(keyword_list) != 0:
            print("Extracting keywords from keyword list and processing them through spacy......")
            user_keywords = process_user_keywords_str(keyword_list, project_path)
            for keyword in user_keywords:
                keyword.origin = ["keyword_list"]
            print("Getting keyword pos using eng_dict dictionary......")
            keyword_list_keywords = verify_words_with_eng_dict(user_keywords, project_path, master_exempt_contained_words)
            with open(keyword_list_keywords_json_fp, "wb+") as out_file:
                out_file.write(json.dumps(keyword_list_keywords, option=json.OPT_INDENT_2))
        else:
            keyword_list_keywords = []

    # Check if sentences exists and create keywords from sentences
    sentence_keywords = []
    if os.path.exists(sentences_tsv_fp):
        sentences = open(sentences_tsv_fp, "r").read()

        if len(sentences) != 0:
            # Filter out unique lines from source data containing sentences
            print("Finding unique lines...")
            unique_lines = sorted(set(sentences.splitlines()))
            # Run lines through Spacy to obtain keywords and categorize them according to their POS
            print("Extracting keywords from sentences using spacy...")
            sentence_keywords = process_text_with_spacy(unique_lines)
            for keyword in sentence_keywords:
                keyword.origin = ["sentences"]
            print("Verifying keyword pos using eng_dict dictionary......")
            sentence_keywords = verify_words_with_eng_dict(sentence_keywords, project_path, master_exempt_contained_words)
            with open(sentences_keywords_json_fp, "wb+") as out_file:
                out_file.write(json.dumps(sentence_keywords, option=json.OPT_INDENT_2))

    # Quit if both files are empty
    if sentences == None and keyword_list == None:
        print('No sentences and keywords detetcted! Please add source data to the "data" folder.')
        quit()

    # Combine keywords from sentences and keyword lists:
    if sentences != None and keyword_list != None:
        for keyword_obj in sentence_keywords:
            if keyword_obj in keyword_list_keywords:
                kw_index = keyword_list_keywords.index(keyword_obj)
                keyword_obj = copy.deepcopy(keyword_obj)
                keyword_obj.origin.append("keyword_list")
                keyword_obj.preferred_pos=keyword_list_keywords[kw_index].preferred_pos
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
        for keyword_obj in keyword_list_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
    elif sentences != None:
        for keyword_obj in sentence_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
    elif keyword_list != None:
        for keyword_obj in keyword_list_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)

    # Rank keywords using Yake:
    print("Extracting keywords using yake...")
    yake_keywords_dict = keyword_extractor(output_fp=yake_tmp_json_fp, sentences=sentences, keywords=keyword_list)

    # Get translated keywords:
    print("Translating keywords to Latin...")
    yake_keywords_list = list(yake_keywords_dict.keys())
    tmp_fp = f"{project_path}/tmp/keyword_generator/{project_id}_tmp.txt"
    with open(tmp_fp, "wb+") as out_file:
        out_file.write("\n".join(yake_keywords_list).encode())
    # google_translate_dict = get_translation(yake_keywords_list, gootrans_tmp_json_fp)

    all_keywords_list = []
    for kw in all_keywords:
        kw.keyword_class = "prime"
        if kw.keyword in yake_keywords_dict.keys():
            kw.yake_score = str(yake_keywords_dict[kw.keyword][1])
            kw.yake_rank = yake_keywords_dict[kw.keyword][0]
        all_keywords_list.append(kw)

    all_keywords_list = sorted(all_keywords_list, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    with open(rated_kw_tmp_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(all_keywords_list, option=json.OPT_INDENT_2))

    # Run keywords through keywords filter
    print("Running keywords through keyword filter...")
    keywords, other_keywords = filter_keywords(all_keywords_list)

    # Convert keyword list into keyword dict
    for keyword_obj in keywords:
        keyword_str = keyword_obj.keyword
        pos_str = keyword_obj.pos
        if keyword_str not in all_keywords_dict.keys():
            all_keywords_dict[keyword_str] = {}
            all_keywords_dict[keyword_str][pos_str] = keyword_obj
        elif pos_str not in all_keywords_dict[keyword_str].keys():
            all_keywords_dict[keyword_str][pos_str] = keyword_obj

    # Shortlist keywords if keyword shortlist exists
    print("Shortlisting keywords...")
    if os.path.exists(excel_output_fp):        
        sheets = ["nouns", "verbs", "adjectives", "adverbs"]
        old_data_fp = convert_excel_to_json(excel_output_fp, target_sheets=sheets, output_json_fp=keywords_json_fp, convert_list=True)
        with open(old_data_fp) as keyword_file:
            keyword_data = json.loads(keyword_file.read())
        keyword_shortlist = generate_keyword_shortlist(keyword_data)
        for keyword_obj in keyword_shortlist:
            keyword_str = keyword_obj.keyword
            pos_str = keyword_obj.pos
            keyword_shortlist_str = keyword_obj.shortlist
            if keyword_str in all_keywords_dict.keys() and pos_str in all_keywords_dict[keyword_str].keys():
                all_keywords_dict[keyword_str][pos_str].shortlist = keyword_shortlist_str
    else:
        shortlist = {}
        shortlist["noun"] = 0
        shortlist["noun_limit"] = 20
        shortlist["verb"] = 0
        shortlist["verb_limit"] = 10
        shortlist["adjective"] = 0
        shortlist["adjective_limit"] = 10
        required_pos = ["noun", "verb", "adjective"]

        for keyword_str, keyword_obj in all_keywords_dict.items():
            pos_list = list(keyword_obj.keys())
            try:
                eng_dict_pos = keyword_obj[pos_list[0]].eng_dict_pos[0]
            except IndexError:
                eng_dict_pos = None
            origin = keyword_obj[pos_list[0]].origin

            if "keyword_list" in origin and eng_dict_pos in pos_list:
                all_keywords_dict[keyword_str][eng_dict_pos].shortlist = "s"
            elif eng_dict_pos in required_pos and eng_dict_pos in pos_list:
                all_keywords_dict[keyword_str][eng_dict_pos].shortlist = "s"
                shortlist[eng_dict_pos] = shortlist[eng_dict_pos] + 1
                if shortlist[eng_dict_pos] == shortlist[eng_dict_pos + "_limit"]:
                    required_pos.remove(eng_dict_pos)

    print("Sorting keywords and exporting files...")
    sorted_keywords_dict = {k: all_keywords_dict[k] for k in sorted(all_keywords_dict.keys())}
    with open(keywords_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(sorted_keywords_dict, option=json.OPT_INDENT_2))

    # Update and export contained words list
    push_contained_words_list(sorted_keywords_dict, master_exempt_contained_words)

    # Excel output for reference only: remove for production
    print(f"Exporting {project_id}_keywords.xlsx...")
    excel_output_list_noun = []
    excel_output_list_verb = []
    excel_output_list_adjective = []
    excel_output_list_adverb = []

    for keyword_data in all_keywords_dict.values():
        for pos, data in keyword_data.items():
            if pos == "noun":
                excel_output_list_noun.append(data)
            elif pos == "verb": 
                excel_output_list_verb.append(data)
            elif pos == "adjective": 
                excel_output_list_adjective.append(data)
            elif pos == "adverb": 
                excel_output_list_adverb.append(data)

    # excel_output_list_noun = sorted(excel_output_list_noun, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    # excel_output_list_verb = sorted(excel_output_list_verb, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    # excel_output_list_adjective = sorted(excel_output_list_adjective, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    # excel_output_list_adverb = sorted(excel_output_list_adverb, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    excel_output_other_keywords = sorted(other_keywords, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))

    # Add sheet for additional keywords
    excel_output_list_additional_keywords = []
    user_keyword_bank = pull_user_keyword_bank(project_path)
    keyword_obj: Preferred_Keyword
    for keyword_obj in user_keyword_bank:
        if "additional_keywords" in keyword_obj.origin:
            dict_data = {"keyword": keyword_obj.keyword, "preferred_pos": keyword_obj.preferred_pos, "disable": keyword_obj.disable}
            excel_output_list_additional_keywords.append(dict_data)
    len_output = len(excel_output_list_additional_keywords)
    dict_data = {"keyword": None, "preferred_pos": None, "disable": None}
    for x in range(200-len_output):
        excel_output_list_additional_keywords.append(dict_data)

    df1 = pd.DataFrame.from_dict(excel_output_list_noun, orient="columns")
    df2 = pd.DataFrame.from_dict(excel_output_list_verb, orient="columns")
    df3 = pd.DataFrame.from_dict(excel_output_list_adjective, orient="columns")
    df4 = pd.DataFrame.from_dict(excel_output_list_adverb, orient="columns")
    df5 = pd.DataFrame.from_dict(excel_output_other_keywords, orient="columns")
    df6 = pd.DataFrame.from_dict(excel_output_list_additional_keywords, orient="columns")

    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')

    sheet_names = [
        'nouns',
        'verbs',
        'adjectives',
        'adverbs',
        'other',
        'additional keywords'
    ]

    df1.to_excel(writer, sheet_name=sheet_names[0])
    df2.to_excel(writer, sheet_name=sheet_names[1])
    df3.to_excel(writer, sheet_name=sheet_names[2])
    df4.to_excel(writer, sheet_name=sheet_names[3])
    df5.to_excel(writer, sheet_name=sheet_names[4])
    df6.to_excel(writer, sheet_name=sheet_names[5])

    workbook  = writer.book

    for sheet_name in sheet_names:
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column(1, 19, 15)
    writer.save()

if __name__ == "__main__":
    generate_word_list(sys.argv[1])
