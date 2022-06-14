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

        if keyword["shortlist"] is not None and keyword["shortlist"] != "":

            keyword_obj = Keyword(
                origin=keyword["origin"],
                source_word=keyword["source_word"],
                spacy_lemma=keyword["spacy_lemma"],
                hard_lemma=keyword["hard_lemma"],
                keyword=keyword["keyword"],
                keyword_len=keyword["keyword_len"],
                spacy_pos=keyword["spacy_pos"],
                wordsAPI_pos=keyword["wordsAPI_pos"],
                pos=keyword["pos"],
                spacy_occurrence=keyword["spacy_occurrence"],
                phonetic_grade=keyword["phonetic_grade"],
                yake_rank=keyword["yake_rank"],
                restrictions_before=isNone(keyword["restrictions_before"].replace(",","").split()),
                restrictions_after=isNone(keyword["restrictions_after"].replace(",","").split()),
                restrictions_as_joint=isNone(keyword["restrictions_as_joint"].replace(",","").split()),
                shortlist=keyword["shortlist"]
            )

            shortlist.append(keyword_obj)

    return shortlist