#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import orjson as json
import pandas as pd
import copy
from typing import List
from classes.keyword_class import Keyword


def create_lemma_keywords(keyword_list: List[Keyword]):

    wordsAPI_dict_fp = "../wordsAPI/cleaned_wordAPI_dict.json"
    with open(wordsAPI_dict_fp) as wordsAPI_dict_file:
        wordsAPI_dict = json.loads(wordsAPI_dict_file.read())

    keyword_list_with_lemma = []

    for keyword_obj in keyword_list:

        keyword_list_with_lemma.append(keyword_obj)

        if keyword_obj.hard_lemma is not None:
            if keyword_obj.hard_lemma["hard_lemma_1"] in wordsAPI_dict.keys():
                keyword_obj_lemma = copy.deepcopy(keyword_obj)
                keyword_obj_lemma.keyword = keyword_obj.hard_lemma["hard_lemma_1"]
                if keyword_obj_lemma not in keyword_list_with_lemma:
                    keyword_list_with_lemma.append(keyword_obj_lemma)
            
            if keyword_obj.hard_lemma["hard_lemma_2"] in wordsAPI_dict.keys():
                keyword_obj_lemma = copy.deepcopy(keyword_obj)
                keyword_obj_lemma.keyword = keyword_obj.hard_lemma["hard_lemma_2"]
                if keyword_obj_lemma not in keyword_list_with_lemma:
                    keyword_list_with_lemma.append(keyword_obj_lemma)

        if (
            keyword_obj.keyword != keyword_obj.spacy_lemma 
            and keyword_obj.spacy_lemma is not None
            and keyword_obj.spacy_lemma in wordsAPI_dict.keys()
        ):
            keyword_obj_lemma = copy.deepcopy(keyword_obj)
            keyword_obj_lemma.keyword = keyword_obj.spacy_lemma
            if keyword_obj_lemma not in keyword_list_with_lemma:
                keyword_list_with_lemma.append(keyword_obj_lemma)

    return keyword_list_with_lemma