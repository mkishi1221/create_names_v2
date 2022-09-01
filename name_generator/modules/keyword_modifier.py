#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword, Modword

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
            keyword_class=keyword_obj.keyword_class,
            shortlist=keyword_obj.shortlist,
            modifier=kw_modifier,
            modword=final_modword,
            modword_len=len(final_modword)
        )
    return modword

def keyword_modifier(keyword_obj: Keyword, kw_modifier: str) -> List[Modword]:
    modword_obj_list = None
    if kw_modifier == "ab_cut":
        modwords = keyword_obj.abbreviations
        if modwords is not None:
            modword_obj_list = []
            for modword in modwords:
                modword_obj = create_modword_obj(keyword_obj, kw_modifier, modword)
                if modword_obj is not None:
                    modword_obj_list.append(modword_obj)
    elif kw_modifier == "no_cut":
        modword = keyword_obj.keyword
        modword_obj = create_modword_obj(keyword_obj, kw_modifier, modword)
        if modword_obj is not None:
            modword_obj_list = [modword_obj]
    return modword_obj_list