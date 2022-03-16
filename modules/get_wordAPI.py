#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from ast import keyword
import orjson as json
from typing import List
from classes.keyword import Keyword
import regex as re
import copy


def create_small_wordAPI(keywords: List[Keyword], wordapi_data: dict):

    # Create smaller portable version of wordAPI dictionary containing words in the source data.
    # Add "keyword" to word list. Dictionary will comprise of words in this word list.
    # If lowercase "lemma" is different to lowercase "keyword", add to word list as well
    
    word_list = []
    for keyword_obj in keywords:
        word_base = str(keyword_obj.keyword)
        word_list.append(word_base)

        word_lemma = str(keyword_obj.spacy_lemma)
        if word_lemma != "" and word_lemma.lower() != word_base:
            word_list.append(word_lemma)

    # Get all dictionary data listed for each word
    small_wordsAPI = {
        word: wordapi_data[word] for word in word_list if word in wordapi_data.keys()
    }

    return small_wordsAPI


def fetch_pos_wordAPI(word: str, wordapi_data: dict):

    # Get all "parts of speech" (pos) associated with each keyword.
    # If keyword is not in wordsAPI dictionary, return pos as empty string.
    pos_list = []

    # Check if keyword is a number (Integer and float). If number, pos is NUM.
    # Potential bug: non-number things are also being flagged as NUM
    if re.match(r'^[\d|\d\.\d]*$', word or "") is not None:
        pos_list.append("NUM")

    # Check if keyword is in wordsAPI dictionary.
    elif word in wordapi_data.keys():
        if "definitions" in wordapi_data[word].keys():
            def_list = wordapi_data[word]["definitions"]

            # Loop through all the definitions tied to the same keyword.
            # Check if pos data is available, is a string and is not already in pos list.
            # If all above is true, add to pos list. Otherwise return pos as empty string.
            # Potential bug: pos list contains many duplicates
            pos_list = []
            for def_data in def_list:
                if (
                    "partOfSpeech" in def_data.keys()
                    and isinstance(def_data["partOfSpeech"], str)
                    and def_data["partOfSpeech"] not in pos_list
                ):
                    pos_list.append(def_data["partOfSpeech"])

    return pos_list


def update_pos_value(
    keywords_db: List[Keyword], wordsAPI_data: dict
) -> List[Keyword]:

    # Get all possible pos using the fetch_pos_wordAPI function and add different pos variations to keyword list.
    # Do for both keyword and lemma word and collect all possible pos.
    updated_keywords_db = []
    for keyword_data in keywords_db:
        pos_list_keyword_n_lemma = set()
        keyword_b = keyword_data.keyword
        if keyword_b is not None:
            keyword_b_pos = fetch_pos_wordAPI(keyword_b, wordsAPI_data)
            pos_list_keyword_n_lemma.update(keyword_b_pos)

        keyword_l = keyword_data.spacy_lemma
        if keyword_l is not None:
            keyword_l_pos = fetch_pos_wordAPI(keyword_l, wordsAPI_data)
            pos_list_keyword_n_lemma.update(keyword_l_pos)

        # Remove duplicate pos
        pos_list = {pos for pos in pos_list_keyword_n_lemma}

        # Add different pos variations to keyword list.
        # Potential bug: deepcopy required here
        for pos in pos_list:
            keyword_data_update = copy.deepcopy(keyword_data)
            keyword_data_update.wordsAPI_pos = pos
            # Future update will evaluate both spacy_POS and wordAPI_POS for accuracy and determine true POS
            keyword_data_update.pos = pos
            updated_keywords_db.append(keyword_data_update)

    return updated_keywords_db


def verify_words_with_wordsAPI(keywords_db: List[Keyword]) -> List[Keyword]:

    main_wordsAPI_dict_filepath = "../wordsAPI/original_data/wordsapi_list.json"
    small_wordsAPI_dict_filepath = "dict/wordsAPI_compact.json"

    # Check if full wordsAPI dictionary is available.
    # If full wordsAPI dictionary is available, create a smaller version.
    try:
        with open(main_wordsAPI_dict_filepath) as wordsAPI_file:
            wordsAPI_data = json.loads(wordsAPI_file.read())

        small_wordsAPI = create_small_wordAPI(keywords_db, wordsAPI_data)
        with open(small_wordsAPI_dict_filepath, "wb+") as out_file:
            out_file.write(json.dumps(small_wordsAPI, option=json.OPT_INDENT_2))

        # Take in keyword list created by spacy and add wordAPI pos data as well as other pos variations.
        updated_keywords_db = update_pos_value(keywords_db, wordsAPI_data)

    # If full wordsAPI dictionary is not available, use smaller version.
    except FileNotFoundError:
        print(
            "Full wordsAPI dictionary not found. Accessing small wordsAPI dictionary..."
        )
        with open(small_wordsAPI_dict_filepath) as wordapi_file:
            wordsAPI_data = json.loads(wordapi_file.read())

        # Take in keyword list and add wordAPI pos data as well as other pos variations.
        updated_keywords_db = update_pos_value(keywords_db, wordsAPI_data)

    return updated_keywords_db
