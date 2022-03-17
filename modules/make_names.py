#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.algorithm import Algorithm
from classes.name import Name
from classes.keyword import Modword

def name_length_scorer(name_length):
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

def combined_keyword_scorer(score_list):
    return round(sum(score_list) / len(score_list))

def combine_1_word(modword_1_obj, alg, name_key):
    name_c1w = modword_1_obj.modword.title()
    name_length = len(name_c1w)
    name_keyword_score = int(modword_1_obj.keyword_total_score)
    name_length_score = name_length_scorer(name_length)
    name_score = name_keyword_score + int(name_length_score)

    return Name(
        name=name_c1w,
        length=name_length,
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score,
        algorithm=alg,
        keywords=name_key
    )

def combine_2_words(modword_1_obj, modword_2_obj, alg, name_key):
    name_c2w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title()
        ]
    )
    name_length = len(name_c2w)
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
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score,
        algorithm=alg,
        keywords=name_key
    )

def combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, alg, name_key):
    name_c3w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title(),
            modword_3_obj.modword.title(),
        ]
    )
    name_length = len(name_c3w)
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
        keyword_score=name_keyword_score,
        length_score=name_length_score,
        score=name_score,
        algorithm=alg,
        keywords=name_key
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

def make_names(algorithms: list[Algorithm], wordlist: dict) -> dict[list[Name]]:
    '''
    Names are now stored in a list in a dictionary where the dictionary keys are the keywords being used.
    ie. name such as "actnow" and "nowact" will be stored in the list under the same key.
    This is to ensure that similar names and their permutations are stored together and the final name list will contain
    the top x number of list from each key.
    This is to make sure that the final generated name list don't contain names that are too similar to each other.
    If the user wants variations/permutations of a specific name, they can call upon the list stored under the specific group of keywords.
    '''
    name_dict: dict[list[Name]] = {}

    for algorithm in algorithms:
        print(f"Generating names with {algorithm}...")

        algorithm_length = len(algorithm)

        wordlist_1_pos = algorithm.components[0][0]
        wordlist_1_modifier = algorithm.components[0][1]
        wordlist1 = wordlist[wordlist_1_pos]
        if algorithm_length == 1:
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                name_key = keyword_1_obj.keyword
                if name_key not in name_dict.keys():
                    name_dict[name_key] = [combine_1_word(modword_1_obj, repr(algorithm), name_key)]
                else:
                    name_dict[name_key].append(combine_1_word(modword_1_obj, repr(algorithm), name_key))

        elif algorithm_length == 2:
            wordlist_2_pos = algorithm.components[1][0]
            wordlist_2_modifier = algorithm.components[1][1]
            wordlist2 = wordlist[wordlist_2_pos]
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                for keyword_2_obj in wordlist2:
                    modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                    name_key = ", ".join(sorted(list(set([keyword_1_obj.keyword, keyword_2_obj.keyword]))))
                    if name_key not in name_dict.keys():
                        name_dict[name_key] = [combine_2_words(modword_1_obj, modword_2_obj, repr(algorithm), name_key)]
                    else:
                        name_dict[name_key].append(combine_2_words(modword_1_obj, modword_2_obj, repr(algorithm), name_key))

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
                        name_key = ", ".join(sorted(list(set([keyword_1_obj.keyword, keyword_2_obj.keyword, keyword_3_obj.keyword]))))
                        if name_key not in name_dict.keys():
                            name_dict[name_key] = [combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, repr(algorithm), name_key)]
                        else:
                            name_dict[name_key].append(combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, repr(algorithm), name_key))

        else:
            if algorithm_length > 3:
                print("Algorithm contains more than 3 keywords!")
            elif algorithm_length < 1:
                print("Algorithm contains no keywords!")

    # Sort each name list.
    for key, names in name_dict.items():
        sorted_names = sorted(names, key=lambda k: (k.name.lower(), k.length, k.score * -1))
        name_dict[key] = sorted_names

    # Sort name dict by keys.
    sorted_name_dict = {key: name_dict[key] for key in sorted(name_dict.keys())}

    return sorted_name_dict
