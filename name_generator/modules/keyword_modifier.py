#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword, Modword
import regex as re

def create_modword_obj(keyword_obj: Keyword, kw_modifier: str, final_modword: str):
    modword = None
    if len(str(final_modword or "")) > 0:
        modword = Modword(
            origin=keyword_obj.origin,
            source_word=keyword_obj.source_word,
            spacy_lemma=keyword_obj.spacy_lemma,
            nltk_lemma=keyword_obj.nltk_lemma,
            hard_lemma=keyword_obj.hard_lemma,
            spacy_pos=keyword_obj.spacy_pos,
            wordsAPI_pos=keyword_obj.wordsAPI_pos,
            preferred_pos=keyword_obj.preferred_pos,
            keyword_len=keyword_obj.keyword_len,
            spacy_occurrence=keyword_obj.spacy_occurrence,
            contained_words=keyword_obj.contained_words,
            phonetic_grade=keyword_obj.phonetic_grade,
            restrictions_before=keyword_obj.restrictions_before,
            restrictions_after=keyword_obj.restrictions_after,
            restrictions_as_joint=keyword_obj.restrictions_as_joint,
            yake_rank=keyword_obj.yake_rank,
            keyword=keyword_obj.keyword,
            pos=keyword_obj.pos,
            shortlist=keyword_obj.shortlist,
            modifier=kw_modifier,
            modword=final_modword,
            modword_len=len(final_modword)
        )
    
    return modword

def keyword_modifier(keyword_obj: Keyword, kw_modifier: str) -> List[Modword]:
    modword_list = None
    if kw_modifier == "ab_cut":
        modword_list = []
        for final_modword in list(keyword_obj.abbreviations or []):
            modword_list.append(create_modword_obj(keyword_obj, kw_modifier, final_modword))

    elif kw_modifier == "no_cut":
        final_modword = keyword_obj.keyword
        modword_list = [create_modword_obj(keyword_obj, kw_modifier, final_modword)]

    return modword_list