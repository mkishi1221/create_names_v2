#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re
import copy
from modules.generate_hard_lemma import generate_hard_lemma
from modules.pull_wordsAPI import pull_wordsAPI_dict
from nltk.stem import WordNetLemmatizer

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
            all_pos = None
    else:
        all_pos = list(all_pos)
    
    return all_pos

def fetch_pos_wordAPI(keyword_list: List[str], spacy_pos, wordapi_data: dict) -> list[str]:

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is None or not in wordsAPI dictionary, return pos as None.
    numbers_as_str = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"
    ]
    all_pos = set()
    keyword_set = set(keyword_list)

    if len(keyword_set) > 0:
        for keyword in keyword_set:
            # Check if keyword is a number (Integer and float). If number, pos is NUM.
            # Potential bug: non-number things are also being flagged as NUM
            if re.match(r'^[\d|\d\.\d]*$', keyword) or keyword.lower() in numbers_as_str:
                all_pos.add("number")
            else:
                # Check if keyword and it's definition/pos data is in wordsAPI dictionary.
                all_pos.update(check_wordsAPI_dict(keyword, wordapi_data))
        
        if spacy_pos in all_pos:
            all_pos = [spacy_pos]

        if len(all_pos) == 0:
            all_pos = None
    else:
        all_pos = None

    return all_pos

def verify_words_with_wordsAPI(keywords_db: List[Keyword]) -> List[Keyword]:

    wordsAPI_data = pull_wordsAPI_dict()

    # Take in keyword list created by spacy and add wordAPI pos data as well as other pos variations.
    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    hard_lemma = None

    for keyword_obj in keywords_db:

        # Create lemmatizer approximated lemma
        lemmatizer = WordNetLemmatizer()
        nltk_lemma = lemmatizer.lemmatize(keyword_obj.keyword)

        # Convert spacy_pos
        spacy_pos = convert_spacy_pos(keyword_obj.spacy_pos)

        # Collect all pos possibilities
        keyword_list = [keyword_obj.keyword, keyword_obj.spacy_lemma]
        pos_list = fetch_pos_wordAPI(keyword_list, spacy_pos, wordsAPI_data)

        # If no pos is returned, use lemmatizer approximated lemma to generate pos.
        if pos_list is None:
            pos_list = fetch_pos_wordAPI([nltk_lemma], spacy_pos, wordsAPI_data)

        # If still no pos is returned, use hard_lemma to generate pos.
        if pos_list is None:
            hard_lemma = generate_hard_lemma(keyword_obj.keyword)
            if hard_lemma is not None:
                pos_list = fetch_pos_wordAPI_w_hardlemma(hard_lemma, wordsAPI_data)

        # If still no pos is returned, use spacy_pos
        if pos_list is None:
            pos_list = [spacy_pos]

        # Add all pos variants of keyword to keyword list
        if pos_list is not None:
            for pos_str in pos_list:
                valid_pos = {"noun", "adjective", "verb", "adverb"}
                
                # generate final lemma to set as keyword
                if pos_str in valid_pos:
                    keyword = lemmatizer.lemmatize(keyword_obj.keyword,  pos=convert_to_nltk_pos(pos_str))
                else:
                    keyword = nltk_lemma

                if keyword not in wordsAPI_data.keys():
                    keyword = keyword_obj.keyword

                # Create keyword object with updated data
                keyword_obj_update = copy.deepcopy(keyword_obj)
                keyword_obj_update.keyword = keyword
                keyword_obj_update.wordsAPI_pos = pos_str
                keyword_obj_update.pos = pos_str
                keyword_obj_update.nltk_lemma = nltk_lemma
                keyword_obj_update.hard_lemma = hard_lemma
                updated_keywords_db.append(keyword_obj_update)
        else:
            updated_keywords_db.append(keyword_obj)

    return updated_keywords_db
