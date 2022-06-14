#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
import regex as re
from modules.pull_wordsAPI import pull_wordsAPI_dict

def find_contained_words(keyword: str, wordsAPI_dict: dict, exempt: List[str]=None) -> List[str]:

    if exempt == None:
        exempt = []

    wordsAPI_words = wordsAPI_dict.keys()
    contained_words = []
    length = len(keyword)
    print(length)
    capitals = re.compile("[A-Z]")

    try:
        position = length - keyword.find(re.findall(capitals, keyword)[-1]) - 1
        print(position)
        if position <= 4:
            position = 4
    except IndexError:
        position = 4

    for start in range(1, length-position):
        word = keyword[start:].lower()
        if word in wordsAPI_words and word not in exempt:
            contained_words.append((word, f"start: {start}", f"length: {length}", f"position: {position}"))
    
    if len(contained_words) == 0:
        contained_words = None

    return contained_words

print(find_contained_words("IdeaIdeaDo", pull_wordsAPI_dict()))
print(find_contained_words("MakeiDentity", pull_wordsAPI_dict()))
print(find_contained_words("MakeiDentity", pull_wordsAPI_dict()))