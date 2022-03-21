#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from typing import Dict
from classes.algorithm import Algorithm
from classes.algorithm import Component
from classes.name import Name
from classes.keyword import Modword
import regex as re
import copy

def name_length_scorer(name_length: int) -> int:

    # match name_length:

    #     case [5,6]:
    #         name_length_score = 6

    #     case [7,8]:
    #         name_length_score = 4

    #     case [9,10]:
    #         name_length_score = 2

    #     case [11,12,13,14,15]:
    #         name_length_score = 0

    #     case [16,17,18]:
    #         name_length_score = -5

    if name_length <= 6:
        name_length_score = 6
    elif name_length <= 8:
        name_length_score = 4
    elif name_length <= 10:
        name_length_score = 2
    elif name_length <= 15:
        name_length_score = 0
    elif name_length <= 18:
        name_length_score = -5
    else:
        name_length_score = -10
    return name_length_score

def combined_keyword_scorer(score_list: List[int]) -> int:
    return round(sum(score_list) / len(score_list))

def combine_1_word(modword_1_obj: Modword, alg: List[Component]) -> Name:
    name_c1w = modword_1_obj.modword.title()
    name_length = len(name_c1w)
    name_length_score = name_length_scorer(name_length)
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_score = int(name_length_score)
    alg_update = copy.deepcopy(alg)
    alg_update[0].keyword = modword_1_obj.keyword
    alg_update[0].modword = modword_1_obj.modword
    name_keywords = [modword_1_obj.keyword]

    return Name(
        name_lower=name_c1w.lower(),
        name_title=name_c1w,
        length=name_length,
        length_score=name_length_score,
        total_score=name_score,
        keywords=name_keywords,
        algorithm=[alg_update]
    )

def combine_2_words(modword_1_obj: Modword, modword_2_obj: Modword, alg: List[Component]) -> Name:
    name_c2w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title()
        ]
    )
    name_length = len(name_c2w)
    name_length_score = name_length_scorer(name_length)
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_score = int(name_length_score)
    alg_update = copy.deepcopy(alg)
    alg_update[0].keyword = modword_1_obj.keyword
    alg_update[0].modword = modword_1_obj.modword
    alg_update[1].keyword = modword_2_obj.keyword
    alg_update[1].modword = modword_2_obj.modword
    name_keywords = sorted(set([modword_1_obj.keyword, modword_2_obj.keyword]))

    return Name(
        name_lower=name_c2w.lower(),
        name_title=name_c2w,
        length=name_length,
        length_score=name_length_score,
        total_score=name_score,
        keywords=name_keywords,
        algorithm=[alg_update],
    )

def combine_3_words(modword_1_obj: Modword, modword_2_obj: Modword, modword_3_obj: Modword, alg: List[Component]) -> Name:
    name_c3w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title(),
            modword_3_obj.modword.title(),
        ]
    )
    name_length = len(name_c3w)
    name_length_score = name_length_scorer(name_length)
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_score = int(name_length_score)
    alg_update = copy.deepcopy(alg)
    alg_update[0].keyword = modword_1_obj.keyword
    alg_update[0].modword = modword_1_obj.modword
    alg_update[1].keyword = modword_2_obj.keyword
    alg_update[1].modword = modword_2_obj.modword
    alg_update[2].keyword = modword_3_obj.keyword
    alg_update[2].modword = modword_3_obj.modword
    name_keywords = sorted(set([modword_1_obj.keyword, modword_2_obj.keyword, modword_3_obj.keyword]))

    return Name(
        name_lower=name_c3w.lower(),
        name_title=name_c3w,
        length=name_length,
        length_score=name_length_score,
        total_score=name_score,
        keywords=name_keywords,
        algorithm=[alg_update],
    )

def add_to_dict(name_obj: Name, name_dict: dict):

    name_lower = name_obj.name_lower
    name_title = name_obj.name_title

    if name_lower not in name_dict.keys():
        name_dict[name_lower] = {}
        name_dict[name_lower][name_title] = name_obj
    else:
        if name_obj.name_title in name_dict[name_lower].keys():
            name_dict[name_lower][name_title].algorithm.extend(name_obj.algorithm)
            name_dict[name_lower][name_title].keywords.extend(name_obj.keywords)
            name_dict[name_lower][name_title].keywords = sorted(set(name_dict[name_lower][name_title].keywords))

        else:
            name_dict[name_lower][name_title] = name_obj
    
    return name_dict


def keyword_modifier(keyword_obj: Name, kw_modifier: str) -> Modword:
    keyword = keyword_obj.keyword
    num = int(kw_modifier[-1])

    final_modword = keyword_obj.keyword

    if len(keyword) > num:
        if re.search(r'front', kw_modifier):
            final_modword = keyword[:num]
        elif re.search(r'rear', kw_modifier):
            num = num * -1
            final_modword = keyword[num:]

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
        pairing_limitations=keyword_obj.pairing_limitations,
        modifier=kw_modifier,
        modword=final_modword,
        modword_len=len(final_modword)
    )

def make_names(algorithms: List[Algorithm], wordlist: dict) -> Dict[str, List[Name]]:
    '''
    Names are now stored in a list in a dictionary where the dictionary keys are the keywords being used.
    ie. name such as "actnow" and "nowact" will be stored in the list under the same key.
    This is to ensure that similar names and their permutations are stored together and the final name list will contain
    the top x number of list from each key.
    This is to make sure that the final generated name list don't contain names that are too similar to each other.
    If the user wants variations/permutations of a specific name, they can call upon the list stored under the specific group of keywords.
    '''
    name_dict: dict[List[Name]] = {}
    # delete below list after bugfix

    for algorithm in algorithms:
        print(f"Generating names with {algorithm}...")

        algorithm_length = len(algorithm)

        wordlist_1_pos = algorithm.components[0].keyword_type
        wordlist_1_modifier = algorithm.components[0].modifier
        wordlist1 = wordlist[wordlist_1_pos]
        if algorithm_length == 1:
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                name_obj = combine_1_word(modword_1_obj, algorithm.components)
                name_dict = add_to_dict(name_obj, name_dict)

        elif algorithm_length == 2:
            wordlist_2_pos = algorithm.components[1].keyword_type
            wordlist_2_modifier = algorithm.components[1].modifier
            wordlist2 = wordlist[wordlist_2_pos]
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                for keyword_2_obj in wordlist2:
                    modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                    name_obj = combine_2_words(modword_1_obj, modword_2_obj, algorithm.components)
                    name_dict = add_to_dict(name_obj, name_dict)

        elif algorithm_length == 3:
            wordlist_2_pos = algorithm.components[1].keyword_type
            wordlist_2_modifier = algorithm.components[1].modifier
            wordlist2 = wordlist[wordlist_2_pos]
            wordlist_3_pos = algorithm.components[2].keyword_type
            wordlist_3_modifier = algorithm.components[2].modifier
            wordlist3 = wordlist[wordlist_3_pos]
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                for keyword_2_obj in wordlist2:
                    modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                    for keyword_3_obj in wordlist3:
                        modword_3_obj = keyword_modifier(keyword_3_obj, wordlist_3_modifier)
                        name_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, algorithm.components)
                        name_dict = add_to_dict(name_obj, name_dict)

        else:
            if algorithm_length > 3:
                print("Algorithm contains more than 3 keywords!")
            elif algorithm_length < 1:
                print("Algorithm contains no keywords!")

    # Sort each name list.
    for key, names in name_dict.items():

        sorted_names = sorted(names.values(), key=lambda k: (k.total_score * -1, k.length, k.name_lower))
        name_dict[key] = sorted_names

    # Sort name dict by keys.
    sorted_name_dict = {key: name_dict[key] for key in sorted(name_dict.keys())}

    return sorted_name_dict
