#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from typing import Dict
from unicodedata import name
import regex as re
import copy
from classes.algorithm_class import Algorithm
from classes.name_class import Etymology
from classes.name_class import Name
from classes.keyword_class import Modword
from modules.grade_phonetic import grade_phonetic
from modules.word_plausible import word_plausability
from modules.generate_hard_lemma import generate_hard_lemma
from modules.pull_wordsAPI import pull_wordsAPI_dict
from modules.find_contained_words import find_contained_words

def is_word(name: str, wordsAPI_data: dict):

    is_it_word = None
    if name not in wordsAPI_data.keys():
        hard_lemma = generate_hard_lemma(name, "use short")
        if hard_lemma is None:
            is_it_word = "no"
        else:
            hl_1 = hard_lemma["hard_lemma_1"]
            hl_2 = hard_lemma["hard_lemma_2"]

            if hl_1 in wordsAPI_data.keys() or hl_2 in wordsAPI_data.keys():
                is_it_word = "yes"
            else:
                is_it_word = "no"
    else:
        is_it_word = "yes"

    return is_it_word

def categorize_name(modifiers, pos_list):

    text_comps = ["head", "tail", "join", "prefix", "suffix"]
    if any(comp in pos_list for comp in text_comps):
        name_type = "text_comp_name"
    elif all(p == "no_cut" for p in modifiers) and len(modifiers) > 0:
        name_type = "no_cut_name"  
    elif not all(p == "no_cut" for p in modifiers) and len(modifiers) > 0:
        name_type = "cut_name"
    else:
        print("ERROR: Name type classification failed!")
        print(f"Modifiers: {modifiers}")
        print(f"Modifiers: {pos_list}")
        exit()

    return name_type

def combine_1_word(modword_1_obj: Modword) -> Name:

    pos_list = (modword_1_obj.pos)
    modifiers = (modword_1_obj.modifier)
    name_type = categorize_name(modifiers, pos_list)

    return Etymology(
        name_in_title=modword_1_obj.modword.title(),
        keyword_tuple=(modword_1_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        name_type=name_type
    )

def combine_2_words(modword_1_obj: Modword, modword_2_obj: Modword) -> Name:
    name_c2w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title()
        ]
    )
    pos_list = (modword_1_obj.pos, modword_2_obj.pos)
    modifiers = (modword_1_obj.modifier, modword_2_obj.modifier)
    name_type = categorize_name(modifiers, pos_list)

    return Etymology(
        name_in_title=name_c2w,
        keyword_tuple=(modword_1_obj.keyword, modword_2_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        name_type=name_type
    )

def combine_3_words(modword_1_obj: Modword, modword_2_obj: Modword, modword_3_obj: Modword) -> Name:
    name_c3w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title(),
            modword_3_obj.modword.title(),
        ]
    )
    pos_list = (modword_1_obj.pos, modword_2_obj.pos, modword_3_obj.pos)
    modifiers = (modword_1_obj.modifier, modword_2_obj.modifier, modword_3_obj.modifier)
    name_type = categorize_name(modifiers, pos_list)

    return Etymology(
        name_in_title=name_c3w,
        keyword_tuple=(modword_1_obj.keyword, modword_2_obj.keyword, modword_3_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        name_type=name_type
    )

def create_name_obj(etymology_obj: Etymology, name_dict: dict, wordsAPI_data: dict):

    name_lower = etymology_obj.name_in_title.lower()
    if name_lower not in name_dict.keys():
        
        name_dict[name_lower] = Name(
            name_in_lower=name_lower,
            length=len(name_lower),
            phonetic_grade=grade_phonetic(name_lower),
            word_plausibility=word_plausability(name_lower),
            is_word=is_word(name_lower, wordsAPI_data),
            etymologies={etymology_obj}
        )
    else:
        name_dict[name_lower].etymologies.add(etymology_obj)
    
    return name_dict

def keyword_modifier(keyword_obj: Name, kw_modifier: str) -> Modword:
    keyword = keyword_obj.keyword
    try:
        num = int(kw_modifier[-1])
    except ValueError:
        num = 0
    final_modword = keyword_obj.keyword

    # "cut_f4" means "cut out first 4 letters"
    # "cut_r5" means "cut out rear 5 letters"
    if len(keyword) > num:
        if re.search(r'cut_f', kw_modifier):
            final_modword = keyword[:num]
        elif re.search(r'cut_r', kw_modifier):
            num = num * -1
            final_modword = keyword[num:]

        modword = Modword(
            origin=keyword_obj.origin,
            source_word=keyword_obj.source_word,
            spacy_lemma=keyword_obj.spacy_lemma,
            hard_lemma=keyword_obj.hard_lemma,
            keyword=keyword_obj.keyword,
            keyword_len=keyword_obj.keyword_len,
            spacy_pos=keyword_obj.spacy_pos,
            wordsAPI_pos=keyword_obj.wordsAPI_pos,
            pos=keyword_obj.pos,
            spacy_occurrence=keyword_obj.spacy_occurrence,
            yake_rank=keyword_obj.yake_rank,
            restrictions_before=keyword_obj.restrictions_before,
            restrictions_after=keyword_obj.restrictions_after,
            restrictions_as_joint=keyword_obj.restrictions_as_joint,
            modifier=kw_modifier,
            modword=final_modword,
            modword_len=len(final_modword)
        )
    else:
        modword = None

    return modword

def clean_wordlist(wordlist, kw_modifier, before_pos=None, after_pos=None):

    cleaned_wordlist = []
    as_joint_pos = f"{before_pos}<joint>{after_pos}"
    for keyword_obj in wordlist:
        modword_obj = keyword_modifier(keyword_obj, kw_modifier)
        if modword_obj is not None:
            as_joint_list = modword_obj.restrictions_as_joint
            before_list = modword_obj.restrictions_before
            after_list = modword_obj.restrictions_after

            if before_pos is None and after_pos is None:
                cleaned_wordlist.append(modword_obj)

            elif before_list is None and after_list is None and as_joint_list is None:
                cleaned_wordlist.append(modword_obj)

            elif before_pos is None and after_pos is not None:
                if after_list is None or after_pos in after_list:
                    cleaned_wordlist.append(modword_obj)

            elif before_pos is not None and after_pos is None:
                if before_list is None or before_pos in before_list:
                    cleaned_wordlist.append(modword_obj)

            elif before_pos is not None and after_pos is not None and as_joint_list is not None:
                if as_joint_pos in as_joint_list:
                    cleaned_wordlist.append(modword_obj)

            elif before_list is not None and after_list is not None:
                if before_pos in before_list and after_pos in after_list:
                    cleaned_wordlist.append(modword_obj)

            elif after_list is not None:
                if after_pos in after_list:
                    cleaned_wordlist.append(modword_obj)

            elif before_list is not None:
                if before_pos in before_list:
                    cleaned_wordlist.append(modword_obj)

    return cleaned_wordlist

def make_names(algorithms: List[Algorithm], wordlist: dict, wordsAPI_data: dict) -> Dict[str, List[Name]]:
    '''
    Names are now stored in a list in a dictionary where the dictionary keys are the keywords being used.
    ie. name such as "actnow" and "nowact" will be stored in the list under the same key.
    This is to ensure that similar names and their permutations are stored together and the final name list will contain
    the top x number of list from each key.
    This is to make sure that the final generated name list don't contain names that are too similar to each other.
    If the user wants variations/permutations of a specific name, they can call upon the list stored under the specific group of keywords.
    '''
    name_dict: dict[List[Name]] = {}

    for algorithm in algorithms:
        print(f"Generating names with {algorithm}...")
        algorithm_length = len(algorithm)
        wordlist_1_pos = algorithm.components[0].pos
        wordlist_1_modifier = algorithm.components[0].modifier
        wordlist1 = wordlist[wordlist_1_pos]
        
        if algorithm_length == 1:
            modlist1 = clean_wordlist(wordlist=wordlist1, kw_modifier=wordlist_1_modifier)
            for modword_1_obj in modlist1:
                etymology_obj = combine_1_word(modword_1_obj)
                name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        elif algorithm_length == 2:
            wordlist_2_pos = algorithm.components[1].pos
            wordlist_2_modifier = algorithm.components[1].modifier
            modlist1 = clean_wordlist(wordlist=wordlist1, kw_modifier=wordlist_1_modifier, after_pos=wordlist_2_pos)
            modlist2 = clean_wordlist(wordlist=wordlist[wordlist_2_pos], kw_modifier=wordlist_2_modifier, before_pos=wordlist_1_pos)
            for modword_1_obj in modlist1:
                for modword_2_obj in modlist2:
                    etymology_obj = combine_2_words(modword_1_obj, modword_2_obj)
                    name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        elif algorithm_length == 3:
            wordlist_2_pos = algorithm.components[1].pos
            wordlist_2_modifier = algorithm.components[1].modifier
            wordlist_3_pos = algorithm.components[2].pos
            wordlist_3_modifier = algorithm.components[2].modifier
            modlist1 = clean_wordlist(wordlist=wordlist1, kw_modifier=wordlist_1_modifier, after_pos=wordlist_2_pos)
            modlist2 = clean_wordlist(wordlist=wordlist[wordlist_2_pos], kw_modifier=wordlist_2_modifier, before_pos=wordlist_1_pos, after_pos=wordlist_3_pos)
            modlist3 = clean_wordlist(wordlist=wordlist[wordlist_3_pos], kw_modifier=wordlist_3_modifier, before_pos=wordlist_2_pos)
            for modword_1_obj in modlist1:
                for modword_2_obj in modlist2:
                    for modword_3_obj in modlist3:
                        etymology_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj)
                        name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        else:
            if algorithm_length > 3:
                print("Algorithm contains more than 3 keywords!")
            elif algorithm_length < 1:
                print("Algorithm contains no keywords!")

    # Convert sets to lists and sort name dict by keys.
    sorted_name_dict = {}
    name_in_lower_list = sorted(name_dict, key=lambda k: (len(k), k))
    for name_in_lower in name_in_lower_list:
        name_data = copy.deepcopy(name_dict[name_in_lower])
        name_data.etymologies = list(name_data.etymologies)
        sorted_name_dict[name_in_lower] = name_data

    return sorted_name_dict
