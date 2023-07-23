#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re
from nltk.stem import WordNetLemmatizer
from modules.generate_hard_lemma import generate_hard_lemma
from modules.grade_phonetic import score_phonetic
from modules.keyword_abbreviator import keyword_abbreviator
from modules.find_contained_words import find_contained_words
from modules.pull_eng_dict import eng_dict
import copy
from modules.pull_xgram import x_grams

def convert_to_nltk_pos(pos_str: str):
    pos_conversion = {
        "noun": "n",
        "verb": "v",
        "adjective": "a",
        "adverb": "r",
    }
    if pos_str in pos_conversion.keys():
        pos_str = pos_conversion[pos_str]
    else:
        print(f"Passed illegal pos_str: {pos_str}")
        quit()

    return pos_str

def convert_spacy_pos(spacy_pos: str):
    pos_conversion = {
        "NOUN": "noun",
        "VERB": "verb",
        "ADJ": "adjective",
        "ADV": "adverb",
        "DET": "definite article",
        "CCONJ": "conjunction",
        "ADP": "adposition",
        "PART": "preposition",
        "PROPN": "noun",
        "PRON": "pronoun",
        "SCONJ":"subordinating_conjunction",
        "AUX":"auxiliary_verb",
        "PUNCT":"punctuation"
    }
    if spacy_pos is not None and spacy_pos.strip() in pos_conversion.keys():
        spacy_pos = pos_conversion[spacy_pos]

    return spacy_pos

def check_eng_dict(keyword: str, eng_dict: dict, eng_dict_words: list) -> list[str]:
    pos_list = set()
    try:
        data = eng_dict[keyword]["pos_list"]
    except KeyError:
        data = None
    if keyword in eng_dict_words and data is not None:
        pos_list.update(data)
    return list(pos_list)

def fetch_eng_dict_pos_w_hardlemma(hard_lemma: dict, eng_dict: dict, eng_dict_words: list) -> list[str]:

    all_pos_raw = []
    all_pos = []
    potential_pos_1 = []
    potential_pos_2 = []
    hard_lemma_1 = hard_lemma["hard_lemma_1"]
    hard_lemma_2 = hard_lemma["hard_lemma_2"]
    possible_pos = hard_lemma["possible_pos"]
    
    if hard_lemma_1 != None:
        potential_pos_1.extend(check_eng_dict(hard_lemma_1, eng_dict, eng_dict_words))
    if len(potential_pos_1) == 0 and hard_lemma_2 != None:
        potential_pos_2.extend(check_eng_dict(hard_lemma_2, eng_dict, eng_dict_words))

    potential_pos_1_len = len(potential_pos_2)
    potential_pos_2_len = len(potential_pos_2)

    if potential_pos_2_len == 0:
        all_pos_raw = potential_pos_1        
    elif potential_pos_1_len > 0 and potential_pos_2_len > 0:
        if potential_pos_1_len >= potential_pos_2_len:
            range_num = potential_pos_1_len
        else:
            range_num = potential_pos_2_len
        for i in range(range_num):
            try:
                pos_1 = potential_pos_1[i]
                if pos_1 not in all_pos_raw:
                    all_pos_raw.append(pos_1)
                    if pos_1 in possible_pos:
                        all_pos.append(pos_1)
            except IndexError:
                pass
            try:
                pos_2 = potential_pos_2[i]
                if pos_2 not in all_pos_raw:
                    all_pos_raw.append(pos_2)
                    if pos_2 in possible_pos:
                        all_pos.append(pos_2)
            except IndexError:
                pass

    if len(all_pos) == 0:
        if len(all_pos_raw) > 0:
            all_pos = all_pos_raw
    
    return all_pos

def fetch_eng_dict_pos(keyword, eng_dict: dict, eng_dict_words: list) -> list[str]:

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is None or not in eng_dict dictionary, return pos as None.
    numbers_as_str = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"
    ]
    all_pos_raw = []
    not_valid = [None, ""]
    all_pos = []
    if keyword not in not_valid:
        # Check if keyword is a number (Integer and float). If number, pos is NUM.
        # Potential bug: non-number things are also being flagged as NUM
        if re.match('.*\d.*', keyword) or keyword.lower() in numbers_as_str:
            all_pos_raw.append("number")
        # Check if keyword and it's definition/pos data is in eng_dict dictionary.
        all_pos_raw.extend(check_eng_dict(keyword, eng_dict, eng_dict_words))
        for pos in all_pos_raw:
            if pos not in all_pos:
                all_pos.append(pos)
    return list(all_pos)

def verify_words_with_eng_dict(keywords: List[Keyword], project_path: str, exempt_contained_kw: list) -> List[Keyword]:
    
    print("Getting keyword pos using eng_dict dictionary...")
    eng_dict_words: list = list(eng_dict.keys())
    curated_eng_word_list = set(open("name_generator/curated_eng_word_list.txt", "r").read().splitlines())
    xgrams_dict: dict = x_grams

    # Take in keyword list created by spacy and add eng_dict pos data as well as other pos variations.
    # Get all possible pos using the fetch_eng_dict_pos function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    keywords_db = []
    hard_lemma = None

    keyword_obj: Keyword
    for keyword_obj in keywords:

        eng_dict_pos_list = set()
        # Collect all pos possibilities
        eng_dict_pos_list.update(fetch_eng_dict_pos(keyword_obj.keyword, eng_dict, eng_dict_words))
        eng_dict_pos_list.update(fetch_eng_dict_pos(keyword_obj.spacy_lemma, eng_dict, eng_dict_words))

        # If no pos is returned, use lemmatizer approximated lemma to generate pos.
        nltk_lemma = None
        lemmatizer = WordNetLemmatizer()
        nltk_lemma = lemmatizer.lemmatize(keyword_obj.keyword)
        keyword_obj.nltk_lemma = nltk_lemma
        if len(eng_dict_pos_list) == 0:
            eng_dict_pos_list.update(fetch_eng_dict_pos(nltk_lemma, eng_dict, eng_dict_words))

        invalid = [None, "", []]

        # Create spacy_pos
        if keyword_obj.spacy_pos not in invalid:
            spacy_pos = convert_spacy_pos(keyword_obj.spacy_pos)
        else:
            spacy_pos = None

        # If still no pos is returned, use hard_lemma to generate pos.
        if len(eng_dict_pos_list) == 0:
            hard_lemma = generate_hard_lemma(keyword_obj.keyword)
            if hard_lemma is not None:
                eng_dict_pos_list.update(fetch_eng_dict_pos_w_hardlemma(hard_lemma, eng_dict, eng_dict_words))
                keyword_obj.hard_lemma = hard_lemma
                if hard_lemma["hard_lemma_1"] + "s" == keyword_obj.keyword and len(hard_lemma["hard_lemma_1"]) > 1:
                    keyword_obj.keyword = hard_lemma["hard_lemma_1"]

        # If still no pos is returned, but source is from "keyword list", apply default as noun.
        if len(eng_dict_pos_list) == 0 and "keyword_list" in keyword_obj.origin:
            eng_dict_pos_list.add("noun")

        # Generate phonetic grade, pattern
        keyword_obj.phonetic_score, keyword_obj.lowest_phonetic, keyword_obj.implausible_chars = score_phonetic(keyword_obj.keyword, xgrams_dict)

        # Generate possible abbreviations
        if keyword_obj.keyword in eng_dict.keys():
            keyword_obj.components = eng_dict[keyword_obj.keyword]["component_list"]
            keyword_obj.abbreviations = keyword_abbreviator(keyword_obj.keyword, keyword_obj.components, curated_eng_word_list)

        # Add all pos variants of keyword to keyword list. If there is spacy pos in eng_dict_pos_list, use it instead.
        all_pos = set()
        if str(spacy_pos or "invalid") in eng_dict_pos_list:
            all_pos = {spacy_pos}
        elif len(list(eng_dict_pos_list or [])) > 0:
            all_pos = eng_dict_pos_list
        else:
            all_pos = {spacy_pos}

        # Create keywords and add it to updated_keywords_db
        if len(all_pos) != 0:
            for pos_str in all_pos:
                keyword_obj_1 = copy.deepcopy(keyword_obj)
                valid_pos = {"noun", "adjective", "verb", "adverb"}
                # generate final lemma to set as keyword
                if pos_str in valid_pos:
                    nltk_lemma = lemmatizer.lemmatize(keyword_obj_1.keyword,  pos=convert_to_nltk_pos(pos_str))
                if nltk_lemma in eng_dict_words:
                    keyword_obj_1.keyword = nltk_lemma
                keyword_obj_1.contained_words = find_contained_words(keyword=keyword_obj_1.keyword, curated_eng_list=curated_eng_word_list, type="keyword", exempt=exempt_contained_kw)
                keyword_obj_1.eng_dict_pos = sorted(eng_dict_pos_list)
                keyword_obj_1.pos = pos_str
                keywords_db.append(keyword_obj_1)
 
        else:
            if keyword_obj.spacy_lemma not in invalid:
                keyword_obj.keyword = keyword_obj.spacy_lemma
            else:
                keyword_obj.keyword = keyword_obj.source_words[0]
            keyword_obj.contained_words = find_contained_words(keyword=keyword_obj.keyword, curated_eng_list=curated_eng_word_list, type="keyword", exempt=exempt_contained_kw)
            keywords_db.append(keyword_obj)

    return keywords_db

