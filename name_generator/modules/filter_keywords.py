#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re
import copy
from pattern3.text.en import singularize
from modules.pull_wordsAPI import pull_wordsAPI_dict
from modules.find_contained_words import find_contained_words

def isplural(pluralForm):
     singularForm = singularize(pluralForm)
     verdict = True if pluralForm is not singularForm else False
     return verdict, singularForm

def filter_keywords(keywords: List[Keyword]) -> List[Keyword]:
    """
    Filter approved keywords (approved keywords may be the following):
    - Either a noun, verb, or an adjective
    - Not contain any characters except alphabets
    - Word is at least 3 letters
    """
    default_blacklist_fp = "name_generator/dict/default_blacklist.txt"
    blacklist = open(default_blacklist_fp, "r").read().splitlines()
    approved_pos = ["noun", "verb", "adjective", "adverb"]
    illegal_char = re.compile(r"[^a-zA-Z]")
    legal_char = re.compile(r"[a-zA-Z]")
    approved_keywords = []
    other_keywords = []

    for keyword in keywords:

        if keyword.keyword in blacklist:
            keyword.pos = "Stopword"

        if (
            keyword.pos in approved_pos
            and not bool(illegal_char.search(keyword.keyword))
            and keyword.keyword_len > 2
        ):
            approved_keywords.append(keyword)
        else:
            other_keywords.append(keyword)

    return list(set(approved_keywords)), list(set(other_keywords))