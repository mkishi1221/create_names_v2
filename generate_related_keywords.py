#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import orjson as json
import pandas as pd
import copy
from classes.keyword_class import Keyword
from modules.process_text_with_spacy import process_text_with_spacy
from modules.get_wordAPI import verify_words_with_wordsAPI
from modules.filter_keywords import filter_keywords
from modules.create_lemma_keywords import create_lemma_keywords

def add_to_keyword_dict(keyword: str, source: str, keywords_dict: dict, keyword_type: str):
    if source in keywords_dict.keys():
        if keyword_type in keywords_dict[source].keys():
            keywords_dict[source][keyword_type].append(keyword)
        else:
            keywords_dict[source][keyword_type] = [keyword]
    else:
        keywords_dict[source] = {}
        keywords_dict[source][keyword_type] = [keyword]

def pull_related_keywords(data: dict, keyword_seed):

    definitions = []
    keywords_dict = {}

    keyword_sources = [
        "also",
        "attribute",
        "cause",
        "derivation",
        "entails",
        "hasCategories",
        "hasInstances",
        "hasMembers",
        "hasParts",
        "hasSubstances",
        "hasTypes",
        "hasUsages",
        "inCategory",
        "instanceOf",
        "memberOf",
        "partOf",
        "participle",
        "pertainsTo",
        "similarTo",
        "substanceOf",
        "synonyms",
        "typeOf",
        "usageOf",
        "verbGroup"
    ]

    if "definitions" in data.keys():
        for def_data in data["definitions"]:
            if "definition" in def_data.keys():
                if def_data["definition"] is not None:
                    definitions.append(def_data["definition"])
            
            for source in keyword_sources:
                if source in def_data.keys():
                    if type(def_data[source]) is list:
                        for keyword in def_data[source]:
                            if " " in keyword:
                                add_to_keyword_dict(keyword, source, keywords_dict, "compound_keywords")
                            else:
                                add_to_keyword_dict(keyword, source, keywords_dict, "single_keywords")

                    elif type(def_data[source]) is str:
                        if " " in keyword:
                            add_to_keyword_dict(keyword, source, keywords_dict, "compound_keywords")
                        else:
                            add_to_keyword_dict(keyword, source, keywords_dict, "single_keywords")

    raw_all_keywords = []

    print(f"Extracting '{keyword_seed}' definitions and processing them through spacy......")

    if definitions != None and len(definitions) > 0:
        def_keywords = process_text_with_spacy(definitions)
        for keyword_obj in def_keywords:
            keyword_obj = copy.deepcopy(keyword_obj)
            keyword_obj.origin = [f"seed_{keyword_seed}_definition"]
            raw_all_keywords.append(keyword_obj)
    else:
        print(f"No definitions for {keyword_seed}!")

    print(f"Extracting '{keyword_seed}' related keywords and processing them through spacy......")

    for source, data in keywords_dict.items():
        for keyword_type, keyword_list in data.items():
            if keyword_list != None and len(keyword_list) > 0:
                source_keywords = process_text_with_spacy(keyword_list)
                for keyword_obj in source_keywords:
                    keyword_obj = copy.deepcopy(keyword_obj)
                    if keyword_type == "single_keywords":
                        keyword_obj.spacy_pos = None
                    keyword_obj.origin = [f"seed_{keyword_seed}_{source}"]
                    raw_all_keywords.append(keyword_obj)
    
    raw_all_keywords = sorted(raw_all_keywords, key=lambda d: d.keyword)

    prev_keyword_obj = Keyword()
    all_keywords = []
    for keyword_obj in raw_all_keywords:
        if keyword_obj == prev_keyword_obj:
            for origin in keyword_obj.origin:
                if origin not in prev_keyword_obj.origin and origin is not None:
                    prev_keyword_obj.origin.append(origin)
        else:
            if prev_keyword_obj.keyword is not None:
                all_keywords.append(prev_keyword_obj)
            prev_keyword_obj = keyword_obj

    if prev_keyword_obj.keyword is not None:
        all_keywords.append(prev_keyword_obj)


    all_keywords = verify_words_with_wordsAPI(all_keywords)

    all_keywords = create_lemma_keywords(all_keywords)
    if "/" in output_fp:
        discarded_keywords_output_fp = output_fp.replace("/", f"/{keyword_seed}_discarded_")
    else:
        discarded_keywords_output_fp = keyword_seed + "_" + "discarded" + discarded_keywords_output_fp
    all_keywords = filter_keywords(all_keywords, discarded_keywords_output_fp)
    all_keywords = sorted(all_keywords, key=lambda d: d.keyword) 

    return all_keywords


def generate_related_keywords(keyword_seed_list, wordsAPI_dict_fp, output_fp):

    with open(wordsAPI_dict_fp) as wordsAPI_dict_file:
        wordsAPI_dict: dict = json.loads(wordsAPI_dict_file.read())

    all_keywords = []

    for keyword_seed in keyword_seed_list:

        if keyword_seed in wordsAPI_dict.keys():
            data = wordsAPI_dict[keyword_seed]
            def_keywords = pull_related_keywords(data, keyword_seed)
            all_keywords.extend(def_keywords)
            output_fp = output_fp.replace("/", f"/{keyword_seed}_")

            with open(output_fp, "wb+") as out_file:
                out_file.write(json.dumps(def_keywords, option=json.OPT_INDENT_2))

            excel_output_fp = output_fp.replace(".json", ".xlsx")
            df1 = pd.DataFrame.from_dict(def_keywords, orient="columns")
            df1.to_excel(excel_output_fp)

        else:
            print(f"Keyword seed '{keyword_seed}' not found in dict!")

    with open(output_fp, "wb+") as out_file:
        out_file.write(json.dumps(def_keywords, option=json.OPT_INDENT_2))

    excel_output_fp = output_fp.replace(".json", ".xlsx")
    df1 = pd.DataFrame.from_dict(def_keywords, orient="columns")
    df1.to_excel(excel_output_fp)


keyword_seed_list = ["name"]
wordsAPI_dict_fp = "../wordsAPI/cleaned_wordAPI_dict.json"
output_fp = "keywords/related_keywords.json"
generate_related_keywords(keyword_seed_list, wordsAPI_dict_fp, output_fp)