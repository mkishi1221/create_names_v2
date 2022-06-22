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
from modules.verify_words_with_wordsAPI import verify_words_with_wordsAPI
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.convert_excel_to_json import convert_excel_to_json
from modules.filter_keywords import filter_keywords
from modules.yake_keyword_extractor import keyword_extractor
from modules.process_user_keywords import process_user_keywords_str
from modules.pull_user_keyword_bank import pull_user_keyword_bank

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
    keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"

    # output filepaths and filenames:
    excel_output_fp: str = f"{project_path}/results/{project_id}_keywords.xlsx"

    # Set variable defaults
    all_keywords: List[Keyword] = []
    all_keywords_dict: Dict[str, Dict[str, Keyword]] = {}
    keyword_list = None
    sentences = None

    # Check if keywords exists and create keywords from keywords list
    if os.path.exists(keyword_list_tsv_fp):
        keyword_list = open(keyword_list_tsv_fp, "r").read().splitlines()
        if len(keyword_list) != 0:
            print("Extracting keywords from keyword list and processing them through spacy......")
            user_keywords = process_user_keywords_str(keyword_list, project_path)
            for keyword in user_keywords:
                keyword.origin = ["keyword_list"]
            print("Getting keyword pos using wordAPI dictionary......")
            keyword_list_keywords = verify_words_with_wordsAPI(user_keywords, project_path)
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
            print("Verifying keyword pos using wordAPI dictionary......")
            sentence_keywords = verify_words_with_wordsAPI(sentence_keywords, project_path)
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
    all_keywords_list = []
    for kw in all_keywords:
        if kw.keyword in yake_keywords_dict.keys():
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
    # Excel input for prototype only: for production, import directly from json
    if os.path.exists(excel_output_fp):        
        sheets = ["nouns", "verbs", "adjectives", "adverbs"]
        old_data_fp = convert_excel_to_json(excel_output_fp, target_sheets=sheets, output_json_fp=keywords_json_fp)
        with open(old_data_fp) as keyword_file:
            keyword_data = json.loads(keyword_file.read())
        keyword_shortlist = generate_keyword_shortlist(keyword_data)
        for keyword_obj in keyword_shortlist:
            keyword_str = keyword_obj.keyword
            pos_str = keyword_obj.pos
            keyword_shortlist_str = keyword_obj.shortlist
            if keyword_str in all_keywords_dict.keys() and pos_str in all_keywords_dict[keyword_str].keys():
                all_keywords_dict[keyword_str][pos_str].shortlist = keyword_shortlist_str

    print("Sorting keywords and exporting files...")
    sorted_keywords_dict = {k: all_keywords_dict[k] for k in sorted(all_keywords_dict.keys())}
    with open(keywords_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(sorted_keywords_dict, option=json.OPT_INDENT_2))

    # Excel output for reference only: remove for production
    excel_output_list_noun = []
    excel_output_list_verb = []
    excel_output_list_adjective = []
    excel_output_list_adverb = []

    for keyword_data in sorted_keywords_dict.values():
        for pos, data in keyword_data.items():
            if pos == "noun":
                excel_output_list_noun.append(data)
            elif pos == "verb": 
                excel_output_list_verb.append(data)
            elif pos == "adjective": 
                excel_output_list_adjective.append(data)
            elif pos == "adverb": 
                excel_output_list_adverb.append(data)

    excel_output_list_noun = sorted(excel_output_list_noun, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    excel_output_list_verb = sorted(excel_output_list_verb, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    excel_output_list_adjective = sorted(excel_output_list_adjective, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
    excel_output_list_adverb = sorted(excel_output_list_adverb, key=lambda d: (int(d.yake_rank or 1000000000), d.keyword))
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
    df1.to_excel(writer, sheet_name='nouns')
    df2.to_excel(writer, sheet_name='verbs')
    df3.to_excel(writer, sheet_name='adjectives')
    df4.to_excel(writer, sheet_name='adverbs')
    df5.to_excel(writer, sheet_name='other')
    df6.to_excel(writer, sheet_name='additional keywords')
    workbook  = writer.book
    worksheet = writer.sheets['nouns']
    worksheet.set_column(1, 19, 15)
    worksheet = writer.sheets['verbs']
    worksheet.set_column(1, 19, 15)
    worksheet = writer.sheets['adjectives']
    worksheet.set_column(1, 19, 15)
    worksheet = writer.sheets['adverbs']
    worksheet.set_column(1, 19, 15)
    worksheet = writer.sheets['other']
    worksheet.set_column(1, 19, 15)
    worksheet = writer.sheets['additional keywords']
    worksheet.set_column(1, 3, 15)
    writer.save()

if __name__ == "__main__":
    generate_word_list(sys.argv[1])
