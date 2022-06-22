#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
import regex as re

def find_contained_words(keyword: str, wordsAPI_dict: dict, exempt: List[str] = None, keyword_analysis: str = None) -> List[str]:

    # The "exempt" variable removes specific contained words if necessary.

    if exempt == None:
        exempt = []

    wordsAPI_words = wordsAPI_dict.keys()
    contained_words = []
    length = len(keyword)
    capitals = re.compile("[A-Z]")

    if keyword_analysis == None:
        # Analyze names
        try:
            position = length - keyword.find(re.findall(capitals, keyword)[-1]) - 1
            if position <= 4:
                position = 4
        except IndexError:
            position = 4
        
        for index in range(1, length-position):
            word = keyword[index:].lower()
            if word in wordsAPI_words and word not in exempt:
                contained_words.append(word)

    else:
        # Analyze keywords
        for index in range(1, length):
            word = keyword[:index].lower()
            pair_word = keyword[index:].lower()
            if word in wordsAPI_words and pair_word in wordsAPI_words:
                contained_words.append(word)
                contained_words.append(pair_word)
    
    if len(contained_words) == 0:
        contained_words = None

    return contained_words