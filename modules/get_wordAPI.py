#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json
from typing import List
from classes.keyword_class import Keyword
import regex as re
import copy
from modules.generate_hard_lemma import generate_hard_lemma

def check_wordsAPI_dict(keyword: str, wordapi_data: dict) -> list[str]:
    pos_list = []
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
                pos_list.append(def_data["partOfSpeech"])

        return set(pos_list)
    else:
        return pos_list

def fetch_pos_wordAPI_w_hardlemma(keyword_obj: Keyword, wordapi_data: dict) -> list[str]:

    all_pos = []

    hard_lemma_1 = keyword_obj.hard_lemma["hard_lemma_1"]
    hard_lemma_2 = keyword_obj.hard_lemma["hard_lemma_2"]
    possible_pos = keyword_obj.hard_lemma["possible_pos"]
    potential_pos = []
    
    if hard_lemma_1 != None:
        potential_pos.extend(check_wordsAPI_dict(hard_lemma_1, wordapi_data))
        if len(potential_pos) > 0:
            for pos in potential_pos:
                if pos in possible_pos:
                    all_pos.append(pos)

    if len(all_pos) == 0:
        if hard_lemma_2 != None:
            potential_pos.extend(check_wordsAPI_dict(hard_lemma_2, wordapi_data))
            if len(potential_pos) > 0:
                for pos in potential_pos:
                    if pos in possible_pos:
                        all_pos.append(pos)
    
    if len(all_pos) == 0:
        if len(potential_pos) > 0:
            all_pos = potential_pos
        else:
            all_pos = None
    
    else:
        sorted(set(all_pos))
    
    return all_pos



def fetch_pos_wordAPI(keyword_obj: Keyword, wordapi_data: dict) -> list[str]:

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is None or not in wordsAPI dictionary, return pos as None.
    keyword = keyword_obj.keyword
    numbers_as_str = [
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"
    ]

    if keyword is None:
        return None

    # Check if keyword is a number (Integer and float). If number, pos is NUM.
    # Potential bug: non-number things are also being flagged as NUM
    elif re.match(r'^[\d|\d\.\d]*$', keyword) or keyword.lower() in numbers_as_str:
        all_pos = ["number"]
        return all_pos

    else:
        lemma = keyword_obj.spacy_lemma
        keyword_spacy_pos = keyword_obj.spacy_pos
        if keyword_spacy_pos is not None:
            pos_conversion = {
                "NOUN": "noun",
                "VERB": "verb",
                "ADJ": "adjective",
                "ADV": "adverb",
                "DET": "definite article",
                "CCONJ": "conjunction",
                "ADP": "adposition",
                "PART": "preposition"
            }
            if keyword_spacy_pos is not None and keyword_spacy_pos.strip() in pos_conversion.keys():
                keyword_spacy_pos = pos_conversion[keyword_spacy_pos]

        # Check if keyword and it's definition/pos data is in wordsAPI dictionary.
        all_pos = check_wordsAPI_dict(keyword, wordapi_data)

        if lemma is not None and lemma != keyword:
            list(all_pos).extend(check_wordsAPI_dict(lemma, wordapi_data))

        if len(all_pos) > 0:

            if all_pos is not None:
                all_pos = sorted(set(all_pos))

                if keyword_spacy_pos in all_pos:
                    return [keyword_spacy_pos]

        else:
            all_pos = None
    
        return all_pos

def verify_words_with_wordsAPI(keywords_db: List[Keyword]) -> List[Keyword]:

    main_wordsAPI_dict_fp = "../wordsAPI/original_data/wordsapi_list.json"
    with open(main_wordsAPI_dict_fp) as wordsAPI_file:
        wordsAPI_data = json.loads(wordsAPI_file.read())

    # Take in keyword list created by spacy and add wordAPI pos data as well as other pos variations.
    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    for keyword_obj in keywords_db:

        # Generate hard_lemma values

        # Collect all pos possibilities
        pos_list = fetch_pos_wordAPI(keyword_obj, wordsAPI_data)            

        # Add different pos variations to keyword list.
        # Potential bug: deepcopy required here
        if pos_list is not None:
            for pos in pos_list:
                keyword_obj_update = copy.deepcopy(keyword_obj)
                keyword_obj_update.wordsAPI_pos = pos
                keyword_obj_update.pos = pos
                updated_keywords_db.append(keyword_obj_update)

        else:
            # Generate hard_lemma values

            keyword_obj_update = copy.deepcopy(keyword_obj)
            hard_lemma = generate_hard_lemma(keyword_obj.keyword)

            if hard_lemma is not None:
                keyword_obj_hl = copy.deepcopy(keyword_obj)
                keyword_obj_hl.hard_lemma = hard_lemma

                pos_list = fetch_pos_wordAPI_w_hardlemma(keyword_obj_hl, wordsAPI_data)

                if pos_list is not None:
                    for pos in pos_list:
                        keyword_obj_hl_update = copy.deepcopy(keyword_obj_hl)
                        keyword_obj_hl_update.wordsAPI_pos = pos
                        keyword_obj_hl_update.pos = pos
                        updated_keywords_db.append(keyword_obj_hl_update)
                
                else:
                    updated_keywords_db.append(keyword_obj_hl)

            else:
                updated_keywords_db.append(keyword_obj_update)

    return updated_keywords_db
