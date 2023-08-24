#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword, Modword

def create_modword_obj(keyword_obj: Keyword, kw_modifier: str, final_modword: str, shortlist_str: str = None, output_lang: str = "english", translation: str = None ):
    modword = None
    if len(str(final_modword or "")) > 0:

        if output_lang.lower() == "english":
            translation = None

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
            translation=translation,
            shortlist=shortlist_str,
        )
    return modword


def keyword_modifier(keyword_obj: Keyword, kw_modifier: str, translations:dict ) -> List[Modword]:
    vowels = "aiueoy"
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

    elif kw_modifier == "ms_cut":
        translations[keyword_obj.keyword] = {"shortlist_str":"s", "language":"english"}
        modwords = []
        pos_str = keyword_obj.pos
        for keyword, data in translations.items():
            if keyword.endswith("er"):
                modwords.append(keyword[:-2] + "r")
            if keyword.endswith("ing"):
                modwords.append(keyword[:-1])
            if keyword[-1] in vowels:
                replacements = vowels.replace(keyword[-1], "")
                for repl in replacements:
                    modwords.append(keyword[:-1] + repl)
            if keyword[-1] not in vowels and keyword[-1] != "s":
                modwords.append(keyword + keyword[-1])
                for vowel_1 in vowels:
                    modwords.append(keyword + vowel_1)
                    for vowel_2 in vowels:
                        modwords.append(keyword + vowel_1 + vowel_2)
            if len(modwords) > 0:
                for modword in modwords:
                    modword_obj = create_modword_obj(
                        keyword_obj,
                        kw_modifier,
                        modword,
                        data["shortlist_str"],
                        data["language"],
                        keyword
                    )
                    if modword_obj is not None:
                        modword_obj_list.append(modword_obj)

    elif kw_modifier == "no_cut":
        modword = keyword_obj.keyword
        shortlist_str = "s" if keyword_obj.pos != "plural_noun" else None
        modword_obj = create_modword_obj(
            keyword_obj,
            kw_modifier,
            modword,
            shortlist_str,
        )
        if modword_obj is not None:
            modword_obj_list.append(modword_obj)

        for translation, data in translations.items():
            modword_obj = create_modword_obj(
                keyword_obj,
                kw_modifier,
                translation,
                data["shortlist_str"],
                data["language"],
                translation
            )
            if modword_obj is not None:
                modword_obj_list.append(modword_obj)

    if len(modword_obj_list) == 0:
        modword_obj_list = None

    return modword_obj_list