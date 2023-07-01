#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword, Modword
from transliterate import translit
from modules.run_googletrans import get_single_translation
from modules.grade_phonetic import grade_phonetic

def create_modword_obj(keyword_obj: Keyword, kw_modifier: str, final_modword: str, shortlist_str: str = None, output_lang: str = "english" ):
    modword = None
    if len(str(final_modword or "")) > 0:
        modword = Modword(
            origin=keyword_obj.origin,
            source_words=keyword_obj.source_words,
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
            phonetic_score=keyword_obj.phonetic_score,
            lowest_phonetic=keyword_obj.lowest_phonetic,
            components=keyword_obj.components,
            abbreviations=keyword_obj.abbreviations,
            restrictions_before=keyword_obj.restrictions_before,
            restrictions_after=keyword_obj.restrictions_after,
            restrictions_as_joint=keyword_obj.restrictions_as_joint,
            yake_score=keyword_obj.yake_score,
            yake_rank=keyword_obj.yake_rank,
            keyword=keyword_obj.keyword,
            pos=keyword_obj.pos,
            keyword_class=keyword_obj.keyword_class,
            modifier=kw_modifier,
            modword=final_modword,
            modword_len=len(final_modword),
            lang=output_lang,
            shortlist=shortlist_str,
        )
    return modword

def keyword_modifier(keyword_obj: Keyword, kw_modifier: str) -> List[Modword]:
    modword_obj_list = []
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
            for modword in modwords:                
                shortlist_str = "s" if modword in abbreviations else None
                modword_obj = create_modword_obj(keyword_obj, kw_modifier, modword, shortlist_str)
                if modword_obj is not None:
                    modword_obj_list.append(modword_obj)
    elif kw_modifier == "no_cut":
        modword = keyword_obj.keyword
        shortlist_str = "s" if keyword_obj.pos != "plural_noun" else None
        modword_obj = create_modword_obj(
            keyword_obj,
            kw_modifier,
            modword,
            shortlist_str
        )
        if modword_obj is not None:
            modword_obj_list.append(modword_obj)

        output_lang_list = [] #["la", "el"]
        phonetic_grades = ["Phonetic_A", "Phonetic_B"]
        for output_lang in output_lang_list:
            translation, language = get_single_translation(keyword_obj.keyword, "en", output_lang)
            if translation is not None and " " not in translation:
                if output_lang == "el":
                    translation = translit(translation, 'el', reversed=True)
                phonetic_grade, phonetic_pattern = grade_phonetic(translation)
                if phonetic_grade in phonetic_grades:
                    print(f"'{translation}' for '{keyword_obj.keyword}' approved - {phonetic_grade}")
                    modword_obj = create_modword_obj(
                        keyword_obj,
                        kw_modifier,
                        translation,
                        shortlist_str,
                        language
                    )
                    if modword_obj is not None:
                        modword_obj_list.append(modword_obj)
                else:
                    print(f"'{translation}' for '{keyword_obj.keyword}' rejected - {phonetic_grade}")

    if len(modword_obj_list) == 0:
        modword_obj_list = None

    return modword_obj_list