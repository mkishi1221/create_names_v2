#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword
import sys
import orjson as json
from typing import List, Dict
import copy
import os.path
from modules.process_text_with_spacy import process_text_with_spacy
from modules.pull_eng_dict import pull_eng_dict
from modules.pull_xgram import pull_xgrams
from modules.verify_words_with_eng_dict import verify_words_with_eng_dict
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.convert_excel_to_json import convert_excel_to_json
from modules.filter_keywords import filter_keywords
from modules.yake_keyword_extractor import keyword_extractor
from modules.process_user_keywords import process_keyword_list
from modules.manage_contained_words import pull_master_exempt

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
    user_keywords_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_keywords_from_keyword-list.json"
    sentences_keywords_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_keywords_from_sentences.json"
    rated_kw_tmp_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_all_keywords.json"
    yake_tmp_json_fp: str = f"{project_path}/tmp/keyword_generator/{project_id}_yake_keywords.json"
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp: str = f"{project_path}/results/{project_id}_keywords.xlsx"

    # Set variable defaults
    all_keywords: List[Keyword] = []
    all_keywords_dict: Dict[str, Dict[str, Keyword]] = {}
    user_keywords = None
    sentences = None

    # Pull dicts
    master_exempt_contained_words = pull_master_exempt()
    eng_dict = pull_eng_dict()
    eng_dict_words = list(eng_dict.keys())
    xgrams = pull_xgrams()

    # Check if keyword list exists and create keywords from keyword list
    if os.path.exists(keyword_list_tsv_fp):
        raw_keywords = [s for s in open(keyword_list_tsv_fp, "r").read().replace(" ", "\n").splitlines() if s]
        user_keywords = process_keyword_list(raw_keywords)
        user_keywords = verify_words_with_eng_dict(user_keywords, eng_dict, eng_dict_words, xgrams, master_exempt_contained_words)
        with open(user_keywords_json_fp, "wb+") as out_file:
            out_file.write(json.dumps(user_keywords, option=json.OPT_INDENT_2))

    # Check if sentences exists and create keywords from sentences
    sentence_keywords = []
    if os.path.exists(sentences_tsv_fp):
        sentences = open(sentences_tsv_fp, "r").read()

        if len(sentences) != 0:
            # Filter out unique lines from source data containing sentences
            print("Finding unique lines...")
            unique_lines = sorted(set(sentences.splitlines()))
            # Run lines through Spacy to obtain keywords and categorize them according to their POS
            sentence_keywords = process_text_with_spacy(unique_lines)
            for keyword in sentence_keywords:
                keyword.origin = ["sentences"]
            sentence_keywords = verify_words_with_eng_dict(sentence_keywords, eng_dict, eng_dict_words, xgrams, master_exempt_contained_words)
            with open(sentences_keywords_json_fp, "wb+") as out_file:
                out_file.write(json.dumps(sentence_keywords, option=json.OPT_INDENT_2))

    # Quit if both files are empty
    if sentences == None and user_keywords == None:
        print('No sentences and keywords detected! Please add source data to the "data" folder.')
        quit()

    # Combine keywords from sentences and keyword lists:
    if sentences != None and user_keywords != None:
        for keyword_obj in sentence_keywords:
            if keyword_obj in user_keywords:
                kw_index = user_keywords.index(keyword_obj)
                keyword_obj = copy.deepcopy(keyword_obj)
                keyword_obj.origin.append("keyword_list")
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
        for keyword_obj in user_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
    elif sentences != None:
        for keyword_obj in sentence_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)
    elif user_keywords != None:
        for keyword_obj in user_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)

    # Rank keywords using Yake:
    print("Extracting keywords using yake...")
    yake_keywords_dict = keyword_extractor(output_fp=yake_tmp_json_fp, sentences=sentences, keywords=raw_keywords)

    all_keywords_list = []
    for kw in all_keywords:
        kw.keyword_class = "prime"
        if kw.keyword in yake_keywords_dict.keys():
            kw.yake_score = str(yake_keywords_dict[kw.keyword][1])
            kw.yake_rank = yake_keywords_dict[kw.keyword][0]
        all_keywords_list.append(kw)

    all_keywords_list = sorted(all_keywords_list, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword_len, d.keyword))
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
        keyword_data, old_data_fp = convert_excel_to_json(excel_output_fp, target_sheets=sheets, output_json_fp=keywords_json_fp, convert_list=True)
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
                eng_dict_pos_list = [x for x in keyword_obj[pos_list[0]].eng_dict_pos if x in required_pos]
                eng_dict_pos = eng_dict_pos_list[0]
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

    excel_output_other_keywords = sorted(other_keywords, key=lambda d: (d.keyword))

    df1 = pd.DataFrame.from_dict(excel_output_list_noun, orient="columns")
    df2 = pd.DataFrame.from_dict(excel_output_list_verb, orient="columns")
    df3 = pd.DataFrame.from_dict(excel_output_list_adjective, orient="columns")
    df4 = pd.DataFrame.from_dict(excel_output_list_adverb, orient="columns")
    df5 = pd.DataFrame.from_dict(excel_output_other_keywords, orient="columns")

    writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')

    sheet_names = [
        'nouns',
        'verbs',
        'adjectives',
        'adverbs',
        'other',
    ]

    df1.to_excel(writer, sheet_name=sheet_names[0])
    df2.to_excel(writer, sheet_name=sheet_names[1])
    df3.to_excel(writer, sheet_name=sheet_names[2])
    df4.to_excel(writer, sheet_name=sheet_names[3])
    df5.to_excel(writer, sheet_name=sheet_names[4])

    workbook  = writer.book

    for sheet_name in sheet_names:
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column(1, 19, 15)
    writer.save()

if __name__ == "__main__":
    generate_word_list(sys.argv[1])
