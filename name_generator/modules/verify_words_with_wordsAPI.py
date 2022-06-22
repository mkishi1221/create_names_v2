#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
from classes.keyword_class import Preferred_Keyword
import regex as re
from nltk.stem import WordNetLemmatizer
from modules.generate_hard_lemma import generate_hard_lemma
from modules.pull_wordsAPI import pull_wordsAPI_dict
from modules.pull_user_keyword_bank import pull_user_keyword_bank
from modules.grade_phonetic import grade_phonetic
from modules.keyword_abbreviator import keyword_abbreviator
from modules.find_contained_words import find_contained_words

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

def check_wordsAPI_dict(keyword: str, wordapi_data: dict) -> list[str]:
    pos_list = set()
    if keyword in wordapi_data.keys() and "definitions" in wordapi_data[keyword].keys():
        def_list = wordapi_data[keyword]["definitions"]
        # Loop through all the definitions tied to the same keyword.
        # Check if pos data is available, is a string and is not already in pos list.
        # If all above is true, add to pos list. Otherwise return pos as empty string.
        # Potential bug: pos list contains many duplicates
        for def_data in def_list:
            if (
                "partOfSpeech" in def_data.keys()
                and isinstance(def_data["partOfSpeech"], str)
                and def_data["partOfSpeech"] not in pos_list
            ):
                pos_list.add(def_data["partOfSpeech"])

        return list(pos_list)
    else:
        return pos_list

def fetch_pos_wordAPI_w_hardlemma(hard_lemma: dict, wordapi_data: dict) -> list[str]:

    all_pos = set()
    potential_pos = []
    hard_lemma_1 = hard_lemma["hard_lemma_1"]
    hard_lemma_2 = hard_lemma["hard_lemma_2"]
    possible_pos = hard_lemma["possible_pos"]
    
    if hard_lemma_1 != None:
        potential_pos.extend(check_wordsAPI_dict(hard_lemma_1, wordapi_data))
        if len(potential_pos) > 0:
            for pos in potential_pos:
                if pos in possible_pos:
                    all_pos.add(pos)

    if len(all_pos) == 0:
        if hard_lemma_2 != None:
            potential_pos.extend(check_wordsAPI_dict(hard_lemma_2, wordapi_data))
            if len(potential_pos) > 0:
                for pos in potential_pos:
                    if pos in possible_pos:
                        all_pos.add(pos)
    
    if len(all_pos) == 0:
        if len(potential_pos) > 0:
            all_pos = potential_pos
        else:
            all_pos = []
    else:
        all_pos = list(all_pos)
    
    return all_pos

def fetch_pos_wordAPI(keyword, wordapi_data: dict) -> list[str]:

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is None or not in wordsAPI dictionary, return pos as None.
    numbers_as_str = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"
    ]
    all_pos = set()
    not_valid = [None, ""]
    if keyword not in not_valid:
        # Check if keyword is a number (Integer and float). If number, pos is NUM.
        # Potential bug: non-number things are also being flagged as NUM
        if re.match(r'^[\d|\d\.\d]*$', keyword) or keyword.lower() in numbers_as_str:
            all_pos.add("number")
        else:
            # Check if keyword and it's definition/pos data is in wordsAPI dictionary.
            all_pos.update(check_wordsAPI_dict(keyword, wordapi_data))

    return list(all_pos)

def verify_words_with_wordsAPI(keywords_db: List[Keyword], project_path) -> List[Keyword]:

    wordsAPI_data: dict = pull_wordsAPI_dict()
    user_keyword_bank_list  = pull_user_keyword_bank(project_path)

    # Take in keyword list created by spacy and add wordAPI pos data as well as other pos variations.
    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    hard_lemma = None

    keyword_obj: Keyword
    for keyword_obj in keywords_db:

        wordsapi_pos_list = set()
        # Collect all pos possibilities
        wordsapi_pos_list.update(fetch_pos_wordAPI(keyword_obj.keyword, wordsAPI_data))
        wordsapi_pos_list.update(fetch_pos_wordAPI(keyword_obj.spacy_lemma, wordsAPI_data))

        # If no pos is returned, use lemmatizer approximated lemma to generate pos.
        nltk_lemma = None
        lemmatizer = WordNetLemmatizer()
        nltk_lemma = lemmatizer.lemmatize(keyword_obj.keyword)
        keyword_obj.nltk_lemma = nltk_lemma
        if len(wordsapi_pos_list) == 0:
            wordsapi_pos_list.update(fetch_pos_wordAPI(nltk_lemma, wordsAPI_data))

        invalid = [None, "", []]

        # Create spacy_pos
        if keyword_obj.spacy_pos not in invalid:
            spacy_pos = convert_spacy_pos(keyword_obj.spacy_pos)
        else:
            spacy_pos = None

        # Create preferred_pos
        preferred_pos = None
        if Preferred_Keyword(keyword=keyword_obj.keyword) in user_keyword_bank_list:
            kw_index = user_keyword_bank_list.index(Preferred_Keyword(keyword=keyword_obj.keyword))
            user_keyword: Preferred_Keyword = user_keyword_bank_list[kw_index]
            none_value = [None, ""]
            if user_keyword.disable in none_value:
                preferred_pos = user_keyword.preferred_pos
                keyword_obj.preferred_pos = preferred_pos

        # If still no pos is returned, use hard_lemma to generate pos.
        if len(wordsapi_pos_list) == 0:
            hard_lemma = generate_hard_lemma(keyword_obj.keyword)
            if hard_lemma is not None:
                wordsapi_pos_list.update(fetch_pos_wordAPI_w_hardlemma(hard_lemma, wordsAPI_data))
                keyword_obj.hard_lemma = hard_lemma
                if hard_lemma["hard_lemma_1"] + "s" == keyword_obj.keyword:
                    keyword_obj.keyword = hard_lemma["hard_lemma_1"]

        # Generate phonetic grade, pattern
        keyword_obj.phonetic_grade, keyword_obj.phonetic_pattern = grade_phonetic(keyword_obj.keyword)

        # Generate possible abbreviations
        keyword_obj.abbreviations = keyword_abbreviator(keyword_obj.keyword, keyword_obj.phonetic_pattern)

        # Find any contained words
        keyword_obj.contained_words = find_contained_words(keyword_obj.keyword, wordsAPI_data, keyword_analysis="yes")

        # Add all pos variants of keyword to keyword list. If there is a preferred pos or the spacy pos is in wordsapi_pos_list, use them instead.
        all_pos = set()
        if len(list(preferred_pos or [])) > 0:
            all_pos = preferred_pos
        elif str(spacy_pos or "invalid") in wordsapi_pos_list:
            all_pos = {spacy_pos}
        elif len(list(wordsapi_pos_list or [])) > 0:
            all_pos = wordsapi_pos_list
        else:
            all_pos = {spacy_pos}

        if len(all_pos) != 0:
            for pos_str in all_pos:
                valid_pos = {"noun", "adjective", "verb", "adverb"}
                
                # generate final lemma to set as keyword
                if pos_str in valid_pos:
                    nltk_lemma = lemmatizer.lemmatize(keyword_obj.keyword,  pos=convert_to_nltk_pos(pos_str))
                if nltk_lemma in wordsAPI_data.keys():
                    keyword_obj.keyword = nltk_lemma
                keyword_obj.wordsAPI_pos = sorted(wordsapi_pos_list)
                keyword_obj.pos = pos_str
                updated_keywords_db.append(keyword_obj)
 
        else:
            if keyword_obj.spacy_lemma not in invalid:
                keyword_obj.keyword = keyword_obj.spacy_lemma
            else:
                keyword_obj.keyword = keyword_obj.source_word
            updated_keywords_db.append(keyword_obj)

    return updated_keywords_db
