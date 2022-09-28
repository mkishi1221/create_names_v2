#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword

def isNone(variable):
    if len(variable) == 0 or variable == "" or variable == None:
        result = None
    else:
        result = variable
    return result

def convert_to_list(string: str):
    if len(str(string or "")) > 0:
        str_list = string.replace('[', '').replace(']', '').replace('\"', '').replace(' ', '').replace('\'', '').split(",")
    else:
        str_list = None
    return str_list

def generate_keyword_shortlist(keyword_data):

    shortlist = []

    for keyword in keyword_data:
        not_valid = [None, ""]
        if keyword["shortlist"] not in not_valid:

            keyword_obj = Keyword(
                origin=convert_to_list(keyword["origin"]),
                source_word=keyword["source_word"],
                spacy_lemma=keyword["spacy_lemma"],
                nltk_lemma=keyword["nltk_lemma"],
                hard_lemma=keyword["hard_lemma"],
                spacy_pos=keyword["spacy_pos"],
                eng_dict_pos=convert_to_list(keyword["eng_dict_pos"]),
                preferred_pos=convert_to_list(keyword["preferred_pos"]),
                keyword_len=keyword["keyword_len"],
                spacy_occurrence=keyword["spacy_occurrence"],
                contained_words=convert_to_list(keyword["contained_words"]),
                phonetic_pattern=keyword["phonetic_pattern"],
                phonetic_grade=keyword["phonetic_grade"],
                abbreviations=convert_to_list(keyword["abbreviations"]),
                restrictions_before=convert_to_list(keyword["restrictions_before"]),
                restrictions_after=convert_to_list(keyword["restrictions_after"]),
                restrictions_as_joint=convert_to_list(keyword["restrictions_as_joint"]),
                yake_rank=keyword["yake_rank"],
                keyword=keyword["keyword"],
                pos=keyword["pos"],
                keyword_class="prime",
                shortlist=keyword["shortlist"]
            )

            shortlist.append(keyword_obj)

    return shortlist