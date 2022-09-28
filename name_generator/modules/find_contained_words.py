#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
import os
import orjson as json

def find_contained_words(keyword: str, curated_eng_list: list, type: str, exempt: List[str] = None) -> List[str]:

    # The "exempt" variable removes specific contained words if necessary.
    if exempt == None:
        exempt = []

    keyword = keyword.lower()
    contained_words_list = set()
    keyword_len = len(keyword)

    if type == "keyword":
        min_size = 2
    elif type == "name":
        min_size = 4
    else:
        raise Exception(f"Variable 'type' can only be 'keyword or 'name'. Type of '{type}' specified instead.")
    

    for index, letter in enumerate(keyword):
        for length in range(min_size, keyword_len+1):
            contained_word = keyword[index:length]
            if contained_word != "" and contained_word != keyword and len(contained_word) >= min_size:
                if contained_word in curated_eng_list and contained_word not in exempt:
                    contained_words_list.add(contained_word)

    contained_words_list = sorted(contained_words_list)

    if len(contained_words_list) == 0:
        contained_words_list = None

    return contained_words_list