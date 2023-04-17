#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword, Modword

def create_modword_obj(keyword_obj: Keyword, kw_modifier: str, final_modword: str, shortlist_str: str = None):
    modword = None
    if len(str(final_modword or "")) > 0:
        modword = Modword(
            origin=keyword_obj.origin,
            source_word=keyword_obj.source_word,
            spacy_lemma=keyword_obj.spacy_lemma,
            nltk_lemma=keyword_obj.nltk_lemma,
            hard_lemma=keyword_obj.hard_lemma,
            spacy_pos=keyword_obj.spacy_pos,
            eng_dict_pos=keyword_obj.eng_dict_pos,
            keyword_len=keyword_obj.keyword_len,
            spacy_occurrence=keyword_obj.spacy_occurrence,
            contained_words=keyword_obj.contained_words,
            phonetic_pattern=keyword_obj.phonetic_pattern,
            phonetic_grade=keyword_obj.phonetic_grade,
            components=keyword_obj.components,
            abbreviations=keyword_obj.abbreviations,
            restrictions_before=keyword_obj.restrictions_before,
            restrictions_after=keyword_obj.restrictions_after,
            restrictions_as_joint=keyword_obj.restrictions_as_joint,
            yake_score=keyword_obj.yake_score,
            yake_rank=keyword_obj.yake_rank,
            keyword=keyword_obj.keyword,
            pos=keyword_obj.pos,
            preferred_pos=keyword_obj.preferred_pos,
            keyword_class=keyword_obj.keyword_class,
            modifier=kw_modifier,
            modword=final_modword,
            modword_len=len(final_modword),
            shortlist=shortlist_str,
        )
    return modword

def keyword_modifier(keyword_obj: Keyword, kw_modifier: str) -> List[Modword]:
    modword_obj_list = None
    if kw_modifier == "ab_cut":
        keyword_str = keyword_obj.keyword
        pos_str = keyword_obj.pos
        modwords = []
        letters = []
        keyword_len = len(keyword_str)
        if keyword_len > 4 and pos_str != "plural_noun":
            for i in range(1, len(keyword_str)-1):
                letters.append(keyword_str[i])
                modwords.append(keyword_str[:1] + "".join(letters))
        abbreviations = keyword_obj.abbreviations if keyword_obj.abbreviations is not None else []
        if len(modwords) > 0:
            modword_obj_list = []
            for modword in modwords:                
                shortlist_str = "s" if modword in abbreviations else None
                modword_obj = create_modword_obj(keyword_obj, kw_modifier, modword, shortlist_str)
                if modword_obj is not None:
                    modword_obj_list.append(modword_obj)
    elif kw_modifier == "no_cut":
        modword = keyword_obj.keyword
        shortlist_str = "s" if keyword_obj.pos != "plural_noun" else None
        modword_obj = create_modword_obj(keyword_obj, kw_modifier, modword, shortlist_str)
        if modword_obj is not None:
            modword_obj_list = [modword_obj]
    return modword_obj_list