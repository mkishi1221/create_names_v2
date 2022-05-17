#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword
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

# Pandas input/output for prototype only: remove for production
import pandas as pd


# "text_file" input is a filepath
# "user_keywords_file" input is a filepath
# "output" input is a filepath
def generate_word_list(sentences_fp: str, keyword_list_fp: str, json_output: str):

    all_keywords: List[Keyword] = []
    all_keywords_dict: Dict[str, Dict[str, Keyword]] = {}
    keyword_list = None
    sentences = None

    # Check if keywords exists
    if os.path.exists(keyword_list_fp):
        keyword_list = open(keyword_list_fp, "r").read().splitlines()
        if len(keyword_list) != 0:
            print("Extracting keywords from keyword list and processing them through spacy......")
            # Spacy is used here as well to generate "lemma" values - this form is more commonly found in wordsAPI dictionary
            user_keywords = process_text_with_spacy(sorted(set(keyword_list)))
            for keyword in user_keywords:
                keyword.origin, keyword.spacy_pos, keyword.pos, keyword.spacy_occurrence = ["keyword_list"], None, None, None
            print("Getting keyword pos using wordAPI dictionary......")
            keyword_list_keywords = verify_words_with_wordsAPI(user_keywords)
            with open("tmp/keyword_generator/keywords_from_keyword-list.json", "wb+") as out_file:
                out_file.write(json.dumps(keyword_list_keywords, option=json.OPT_INDENT_2))

    # Check if sentences exists
    if os.path.exists(sentences_fp):
        sentences = open(sentences_fp, "r").read()

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
            sentence_keywords = verify_words_with_wordsAPI(sentence_keywords)
            with open("tmp/keyword_generator/keywords_from_sentences.json", "wb+") as out_file:
                out_file.write(json.dumps(sentence_keywords, option=json.OPT_INDENT_2))

    # Quit if both files are empty
    if sentences == None and keyword_list == None:
        print(
            'No sentences and keywords detetcted! Please add source data to the "data" folder.'
        )
        quit()

    # Combine keywords from sentences and keyword lists:
    if sentences != None and keyword_list != None:
        for keyword_obj in sentence_keywords:
            if keyword_obj in keyword_list_keywords:
                keyword_obj = copy.deepcopy(keyword_obj)
                keyword_obj.origin.append("keyword_list")
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
    yake_keywords_dict = keyword_extractor(sentences=sentences, keywords=keyword_list)
    all_keywords_rated = []
    for kw in all_keywords:
        if kw.keyword in yake_keywords_dict.keys():
            kw.yake_rank = yake_keywords_dict[kw.keyword][0]
            all_keywords_rated.append(kw)
    all_keywords_rated = sorted(all_keywords_rated, key=lambda d: (d.yake_rank, d.keyword))
    with open("tmp/keyword_generator/all_keywords.json", "wb+") as out_file:
        out_file.write(json.dumps(all_keywords_rated, option=json.OPT_INDENT_2))

    df1 = pd.DataFrame.from_dict(all_keywords_rated, orient="columns")
    df1.to_excel("tmp/keyword_generator/all_keywords.xlsx")

    # Run keywords through keywords filter
    print("Running keywords through keyword filter...")
    keywords, other_keywords = filter_keywords(all_keywords_rated)

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
    excel_output_fp = json_output.replace(".json", f"_shortlist.xlsx").replace("tmp/keyword_generator/", f"results/")
    if os.path.exists(excel_output_fp):
        
        sheets = ["nouns", "verbs", "adjectives", "adverbs"]
        old_data_fp = convert_excel_to_json(excel_output_fp, target_sheets=sheets)
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
    with open(json_output, "wb+") as out_file:
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

    excel_output_list_noun = sorted(excel_output_list_noun, key=lambda d: (d.yake_rank, d.keyword))
    excel_output_list_verb = sorted(excel_output_list_verb, key=lambda d: (d.yake_rank, d.keyword))
    excel_output_list_adjective = sorted(excel_output_list_adjective, key=lambda d: (d.yake_rank, d.keyword))
    excel_output_list_adverb = sorted(excel_output_list_adverb, key=lambda d: (d.yake_rank, d.keyword))
    excel_output_other_keywords = sorted(other_keywords, key=lambda d: (d.yake_rank, d.keyword))

    df1 = pd.DataFrame.from_dict(excel_output_list_noun, orient="columns")
    df2 = pd.DataFrame.from_dict(excel_output_list_verb, orient="columns")
    df3 = pd.DataFrame.from_dict(excel_output_list_adjective, orient="columns")
    df4 = pd.DataFrame.from_dict(excel_output_list_adverb, orient="columns")
    df5 = pd.DataFrame.from_dict(excel_output_other_keywords, orient="columns")

    writer = pd.ExcelWriter(excel_output_fp)
    df1.to_excel(writer, sheet_name='nouns')
    df2.to_excel(writer, sheet_name='verbs')
    df3.to_excel(writer, sheet_name='adjectives')
    df4.to_excel(writer, sheet_name='adverbs')
    df5.to_excel(writer, sheet_name='other')
    writer.save()

if __name__ == "__main__":
    generate_word_list(sys.argv[1], sys.argv[2], sys.argv[3])
