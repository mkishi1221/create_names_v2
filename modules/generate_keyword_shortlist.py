#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword_class import Keyword

def generate_keyword_shortlist(keyword_data):

    shortlist = []

    for keyword in keyword_data:

        if keyword["shortlist"] is not None and keyword["shortlist"] != "":
            keyword_obj = Keyword(
                origin=keyword["origin"],
                source_word=keyword["source_word"],
                spacy_lemma=keyword["spacy_lemma"],
                keyword=keyword["keyword"],
                keyword_len=keyword["keyword_len"],
                spacy_pos=keyword["spacy_pos"],
                wordsAPI_pos=keyword["wordsAPI_pos"],
                pos=keyword["pos"],
                spacy_occurrence=keyword["spacy_occurrence"],
                pairing_limitations=keyword["pairing_limitations"],
                shortlist=keyword["shortlist"]
            )

            shortlist.append(keyword_obj)

    return shortlist