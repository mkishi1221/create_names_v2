#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re
import copy
from pattern3.text.en import singularize
from modules.pull_wordsAPI import pull_wordsAPI_dict
from modules.grade_phonetic import grade_phonetic
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
    default_blacklist_fp = "dict/default_blacklist.txt"
    blacklist = open(default_blacklist_fp, "r").read().splitlines()
    approved_pos = ["noun", "verb", "adjective", "adverb"]
    illegal_char = re.compile(r"[^a-zA-Z]")
    legal_char = re.compile(r"[a-zA-Z]")
    approved_keywords = []
    other_keywords = []

    wordsAPI_data = pull_wordsAPI_dict()

    pos_conversion = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJ": "adjective",
    "ADV": "adverb",
    "DET": "definite article",
    "CCONJ": "conjunction",
    "ADP": "adposition",
    "PART": "preposition",
    "PRON": "pronoun",
    "PROPN": "noun",
    }

    for keyword in keywords:
    
        keyword.phonetic_grade = grade_phonetic(keyword.keyword)

        if keyword.pos is None:
            if keyword.spacy_pos is not None:
                spacy_pos = keyword.spacy_pos

                if spacy_pos in pos_conversion.keys():
                    conv_pos = pos_conversion[spacy_pos]
                    keyword = copy.deepcopy(keyword)
                    keyword.pos = conv_pos
        
        if keyword.pos == "noun":
            verdict, singularForm = isplural(keyword.keyword)
            if verdict == True and singularForm in wordsAPI_data.keys():
                keyword = copy.deepcopy(keyword)
                keyword.keyword = singularForm
        
        # if keyword.pos == "verb" or keyword.pos == "adjective":
        #     if keyword.spacy_lemma in wordsAPI_data.keys():
        #         keyword = copy.deepcopy(keyword)
        #         keyword.keyword = keyword.spacy_lemma

        keyword.contained_words = find_contained_words(keyword.keyword, wordsAPI_data)

        if keyword.keyword in blacklist:
            keyword = copy.deepcopy(keyword)
            keyword.pos = "Stopword"

        if (
            keyword.pos in approved_pos
            and not bool(illegal_char.search(keyword.keyword))
            and keyword.keyword_len > 2
        ):
            approved_keywords.append(keyword)
        elif bool(legal_char.search(keyword.keyword)):
            other_keywords.append(keyword)

    return list(set(approved_keywords)), list(set(other_keywords))