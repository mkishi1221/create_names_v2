#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import orjson as json
from typing import List

def pull_wordsAPI_dict():

    main_wordsAPI_dict_fp = "../wordsAPI/cleaned_wordAPI_dict.json"
    with open(main_wordsAPI_dict_fp) as wordsAPI_file:
        wordsAPI_data = json.loads(wordsAPI_file.read())

    return wordsAPI_data

def find_contained_words(keyword):
    wordAPI_words = pull_wordsAPI_dict().keys()
    contained_words_list = set()

    for index, letter in enumerate(keyword):
        for length in range(2, len(keyword)):
            contained_word = keyword[index:length+1]
            print(contained_word)
            if contained_word != "" and contained_word != keyword:
                print("pass1")
                if contained_word in wordAPI_words:
                    contained_words_list.add(contained_word)
                    print("pass2")

    print(contained_words_list)

    return contained_words_list

def find_contained_words_test(keyword: str, wordsAPI_words: list, exempt: List[str] = None) -> List[str]:

    # The "exempt" variable removes specific contained words if necessary.
    if exempt == None:
        exempt = []

    keyword = keyword.lower()
    contained_words_list = set()
    keyword_len = len(keyword)

    min_size = 4
    for index, letter in enumerate(keyword):
        for length in range(min_size, keyword_len+1):
            contained_word = keyword[index:length]
            print(length, contained_word)
            if contained_word != "" and contained_word != keyword and len(contained_word) >= min_size:
                # print(contained_word)
                if contained_word in wordsAPI_words and contained_word not in exempt:
                    contained_words_list.add(contained_word)

    contained_words_list = sorted(contained_words_list)
    
    if len(contained_words_list) == 0:
        contained_words_list = None

    return contained_words_list

# find_contained_words("Masayuki")

print(find_contained_words_test("masayuki", pull_wordsAPI_dict().keys()))