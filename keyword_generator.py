#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword
import sys
import orjson as json
from typing import List, Dict
import regex as re
import copy
import os.path
from modules.process_text_with_spacy import process_text_with_spacy
from modules.get_wordAPI import verify_words_with_wordsAPI
from modules.generate_keyword_shortlist import generate_keyword_shortlist
from modules.convert_excel_to_json import convert_excel_to_json
from modules.filter_keywords import filter_keywords
from modules.create_lemma_keywords import create_lemma_keywords

# Pandas input/output for prototype only: remove for production
import pandas as pd


# "text_file" input is a filepath
# "user_keywords_file" input is a filepath
# "output" input is a filepath
def generate_word_list(sentences_fp: str, keyword_list_fp: str, json_output: str):

    all_keywords: List[Keyword] = []
    all_keywords_dict: Dict[str, Dict[str, Keyword]] = {}

    # Check if keywords exists
    user_keywords = open(keyword_list_fp, "r").read().splitlines()
    if len(user_keywords) != 0:

        print("Extracting keywords from keyword list and processing them through spacy......")
        # Spacy is used here as well to generate "lemma" values - this form is more commonly found in wordsAPI dictionary
        user_keywords = sorted(set(user_keywords))
        user_keywords = process_text_with_spacy(user_keywords)
        for keyword in user_keywords:
            keyword.origin = ["keyword_list"]
            keyword.spacy_pos = None
            keyword.pos = None
            keyword.spacy_occurrence = None

        print("Getting keyword pos using wordAPI dictionary......")
        keyword_list_keywords = verify_words_with_wordsAPI(user_keywords)
        keyword_list_keywords = create_lemma_keywords(keyword_list_keywords)

        with open("ref/keywords_from_keyword-list.json", "wb+") as out_file:
            out_file.write(json.dumps(keyword_list_keywords, option=json.OPT_INDENT_2))

    # Check if sentences exists
    sentences = open(sentences_fp, "r").read().splitlines()
    if len(sentences) != 0:

        # Filter out unique lines from source data containing sentences
        print("Finding unique lines...")
        unique_lines = sorted(set(sentences))

        # Run lines through Spacy to obtain keywords and categorize them according to their POS
        print("Extracting keywords from sentences using spacy...")
        sentence_keywords = process_text_with_spacy(unique_lines)
        for keyword in sentence_keywords:
            keyword.origin = ["sentences"]

        print("Verifying keyword pos using wordAPI dictionary......")
        sentence_keywords = verify_words_with_wordsAPI(sentence_keywords)
        sentence_keywords = create_lemma_keywords(sentence_keywords)

        for keyword_obj in sentence_keywords:
            if keyword_obj in keyword_list_keywords:
                keyword_obj.origin.append("keyword_list")
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)

        for keyword_obj in keyword_list_keywords:
            if keyword_obj not in all_keywords:
                all_keywords.append(keyword_obj)

        with open("ref/keywords_from_sentences.json", "wb+") as out_file:
            out_file.write(json.dumps(sentence_keywords, option=json.OPT_INDENT_2))

    # Quit if both files are empty
    if sentences == "" and len(user_keywords) == 0:
        print(
            'No sentences and keywords detetcted! Please add source data to the "data" folder.'
        )
        quit()

    # Run keywords through keywords filter
    print("Running keywords through keyword filter...")
    discarded_keywords_output_fp = json_output.replace("/", "/discarded_")
    keywords = filter_keywords(all_keywords, discarded_keywords_output_fp)

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
    old_excel_output = "".join([json_output[:-5], ".xlsx"])
    if os.path.exists(old_excel_output):
        
        sheet_name = "Sheet1"
        old_excel_output = convert_excel_to_json(old_excel_output, sheet_name)   

        with open(old_excel_output) as keyword_file:
            keyword_data = json.loads(keyword_file.read())

        keyword_shortlist = generate_keyword_shortlist(keyword_data)

        for keyword_obj in keyword_shortlist:
            keyword_str = keyword_obj.keyword
            pos_str = keyword_obj.pos
            keyword_shortlist = keyword_obj.shortlist
            if keyword_str in all_keywords_dict.keys():
                if pos_str in all_keywords_dict[keyword_str].keys():
                    all_keywords_dict[keyword_str][pos_str].shortlist = keyword_shortlist

    print("Sorting keywords and exporting files...")

    all_keywords_dict = {k: all_keywords_dict[k] for k in sorted(all_keywords_dict.keys())}
    # sorted_keywords_dict = {}
    # for k in sorted(all_keywords_dict, key=len):
    #     sorted_keywords_dict[k] = all_keywords_dict[k]

    sorted_keywords_dict = all_keywords_dict
    
    with open(json_output, "wb+") as out_file:
        out_file.write(json.dumps(sorted_keywords_dict, option=json.OPT_INDENT_2))

    # Excel output for reference only: remove for production
    excel_output_fp = "".join([json_output[:-5], "_shortlist.xlsx"])
    excel_output_list = []
    for key_1, keyword_pos in sorted_keywords_dict.items():
        for key_2, keyword in keyword_pos.items():
            excel_output_list.append(keyword)
    df1 = pd.DataFrame.from_dict(excel_output_list, orient="columns")
    df1.to_excel(excel_output_fp)

if __name__ == "__main__":
    generate_word_list(sys.argv[1], sys.argv[2], sys.argv[3])
