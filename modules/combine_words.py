#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.algorithm import Algorithm
from classes.name import Name
from classes.keyword import Modword

def name_length_scorer(name_length):
    if name_length <= 6:
        name_length_score = 3
    elif name_length <= 8:
        name_length_score = 2
    elif name_length <= 10:
        name_length_score = 1
    else:
        name_length_score = 0
    return name_length_score

def combined_keyword_scorer(score_list):
    return sum(score_list) / len(score_list)

def combine_1_word(modword_1_obj):

    name_c1w = modword_1_obj.modword.title()

    name_length = len(name_c1w)
    name_keywords = [(modword_1_obj.keyword, modword_1_obj.pos)]
    name_keyword_score = int(modword_1_obj.keyword_total_score)
    name_length_score = name_length_scorer(name_length)
    name_score = name_keyword_score + int(name_length_score)

    return Name(
        name=name_c1w,
        length=name_length,
        keywords=name_keywords,
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score
    )

def combine_2_words(modword_1_obj, modword_2_obj):

    name_c2w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title()
        ]
    )
    name_length = len(name_c2w)
    name_keywords = [(modword_1_obj.keyword, modword_1_obj.pos), (modword_2_obj.keyword, modword_2_obj.pos)]
    name_keyword_score = combined_keyword_scorer(
        [
            int(modword_1_obj.keyword_total_score),
            int(modword_2_obj.keyword_total_score)
        ]
    )
    name_length_score = name_length_scorer(name_length)
    name_score = name_keyword_score + int(name_length_score)

    return Name(
        name=name_c2w,
        length=name_length,
        keywords=name_keywords,
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score
    )

def combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj):

    name_c3w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title(),
            modword_3_obj.modword.title(),
        ]
    )
    name_length = len(name_c3w)
    name_keywords = [
        (modword_1_obj.keyword, modword_1_obj.pos),
        (modword_2_obj.keyword, modword_2_obj.pos),
        (modword_3_obj.keyword, modword_3_obj.pos)
    ]
    name_keyword_score = combined_keyword_scorer(
        [
            int(modword_1_obj.keyword_total_score),
            int(modword_2_obj.keyword_total_score),
            int(modword_3_obj.keyword_total_score)
        ]
    )
    name_length_score = name_length_scorer(name_length)
    name_score = name_keyword_score + int(name_length_score)

    return Name(
        name=name_c3w,
        length=name_length,
        keywords=name_keywords,
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score
    )

def keyword_modifier(keyword_obj: Name, kw_modifier):

    # Needs to be expanded upon to accomodate other modifiers
    if kw_modifier == "no_cut":
        final_modword = keyword_obj.keyword
    return Modword(
        origin=keyword_obj.origin,
        source_word=keyword_obj.source_word,
        spacy_lemma=keyword_obj.spacy_lemma,
        keyword=keyword_obj.keyword,
        keyword_len=keyword_obj.keyword_len,
        spacy_pos=keyword_obj.spacy_pos,
        wordsAPI_pos=keyword_obj.wordsAPI_pos,
        pos=keyword_obj.pos,
        spacy_occurrence=keyword_obj.spacy_occurrence,
        keyword_user_score=keyword_obj.keyword_user_score,
        keyword_wiki_score=keyword_obj.keyword_wiki_score,
        keyword_total_score=keyword_obj.keyword_total_score,
        pairing_limitations=keyword_obj.pairing_limitations,
        modifier=kw_modifier,
        modword=final_modword,
        modword_len=len(final_modword)
    )

def combine_words(algorithm: Algorithm, wordlist: dict) -> List[Name]:

    # Combine keywords from 2 keyword lists
    name_list: list[Name] = []
    algorithm_length = len(algorithm)

    wordlist_1_pos = algorithm.components[0][0]
    wordlist_1_modifier = algorithm.components[0][1]
    wordlist1 = wordlist[wordlist_1_pos]
    if algorithm_length == 1:
        for keyword_1_obj in wordlist1:
            modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
            name_list.append(combine_1_word(modword_1_obj))

    elif algorithm_length == 2:
        wordlist_2_pos = algorithm.components[1][0]
        wordlist_2_modifier = algorithm.components[1][1]
        wordlist2 = wordlist[wordlist_2_pos]
        for keyword_1_obj in wordlist1:
            modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
            for keyword_2_obj in wordlist2:
                modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                name_list.append(combine_2_words(modword_1_obj, modword_2_obj))

    elif algorithm_length == 3:
        wordlist_2_pos = algorithm.components[1][0]
        wordlist_2_modifier = algorithm.components[1][1]
        wordlist2 = wordlist[wordlist_2_pos]
        wordlist_3_pos = algorithm.components[2][0]
        wordlist_3_modifier = algorithm.components[2][1]
        wordlist3 = wordlist[wordlist_3_pos]
        for keyword_1_obj in wordlist1:
            modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
            for keyword_2_obj in wordlist2:
                modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                for keyword_3_obj in wordlist3:
                    modword_3_obj = keyword_modifier(keyword_3_obj, wordlist_3_modifier)
                    name_list.append(combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj))

    else:
        if algorithm_length > 3:
            print("Algorithm contains more than 3 keywords!")
        elif algorithm_length < 1:
            print("Algorithm contains no keywords!")

    # Sort name list by alphabetical order and length.
    name_list.sort(
        key=lambda combined_name: getattr(combined_name, "name").lower(), reverse=False
    )
    sorted_by_len_name_list = sorted(
        name_list,
        key=lambda combined_name: getattr(combined_name, "length"),
        reverse=False,
    )

    return sorted_by_len_name_list
