#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword

def isNone(variable):
    if len(variable) == 0 or variable == "" or variable == None:
        result = None
    else:
        result = variable
    return result

def generate_keyword_shortlist(keyword_data):

    shortlist = []

    for keyword in keyword_data:
        not_valid = [None, ""]
        if keyword["shortlist"] not in not_valid:
            keyword_obj = Keyword(
                origin=keyword["origin"],
                source_word=keyword["source_word"],
                spacy_lemma=keyword["spacy_lemma"],
                nltk_lemma=keyword["nltk_lemma"],
                hard_lemma=keyword["hard_lemma"],
                spacy_pos=keyword["spacy_pos"],
                wordsAPI_pos=keyword["wordsAPI_pos"],
                preferred_pos=keyword["preferred_pos"],
                keyword_len=keyword["keyword_len"],
                spacy_occurrence=keyword["spacy_occurrence"],
                contained_words=keyword["contained_words"],
                phonetic_grade=keyword["phonetic_grade"],
                restrictions_before=isNone(keyword["restrictions_before"].replace(",","").split()),
                restrictions_after=isNone(keyword["restrictions_after"].replace(",","").split()),
                restrictions_as_joint=isNone(keyword["restrictions_as_joint"].replace(",","").split()),
                yake_rank=keyword["yake_rank"],
                keyword=keyword["keyword"],
                pos=keyword["pos"],
                shortlist=keyword["shortlist"]
            )

            shortlist.append(keyword_obj)

    return shortlist