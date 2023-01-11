#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from typing import Dict
import copy
from classes.algorithm_class import Algorithm
from classes.name_class import Etymology
from classes.name_class import Name
from classes.keyword_class import Modword
from modules.grade_phonetic import grade_phonetic
from modules.word_plausible import word_plausability
from modules.generate_hard_lemma import generate_hard_lemma

def is_word(name: str, eng_dict_words: list):

    is_it_word = None
    if name not in eng_dict_words:
        hard_lemma = generate_hard_lemma(name, "use short")
        if hard_lemma is None:
            is_it_word = "no"
        else:
            hl_1 = hard_lemma["hard_lemma_1"]
            hl_2 = hard_lemma["hard_lemma_2"]

            if hl_1 in eng_dict_words or hl_2 in eng_dict_words:
                is_it_word = "yes"
            else:
                is_it_word = "no"
    else:
        is_it_word = "yes"

    return is_it_word

def categorize_name(modifiers, pos_list, fit = None):

    pref_suff_comps = ["prefix", "suffix"]
    text_comps = ["head", "tail", "join"]
    if any(comp in pos_list for comp in text_comps):
        name_type = "text_comp_name"
    elif any(comp in pos_list for comp in pref_suff_comps):
        name_type = "pref_suff_name"
    elif all(p == "no_cut" for p in modifiers) and len(modifiers) > 0:
        name_type = "no_cut_name"
    elif "no_cut" in modifiers and "ab_cut" in modifiers:
        name_type = "part_cut_name"
    elif all(p == "ab_cut" for p in modifiers) and len(modifiers) > 0:
        name_type = "cut_name"
    else:
        raise Exception(f"ERROR: Name type classification failed! Modifiers: {modifiers} / Pos list: {pos_list}")

    if fit != None:
        name_type = fit + name_type

    return name_type

def combine_1_word(modword_1_obj: Modword) -> Name:

    pos_list = (modword_1_obj.pos)
    modifiers = (modword_1_obj.modifier)
    name_type = categorize_name(modifiers, pos_list)

    print(modword_1_obj.keyword, modword_1_obj.keyword_class)

    return Etymology(
        name_in_title=modword_1_obj.modword.title(),
        modword_tuple=(modword_1_obj.modword),
        keyword_tuple=(modword_1_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        exempt_contained= sorted(set(modword_1_obj.contained_words + [modword_1_obj.keyword])),
        keyword_classes= [modword_1_obj.keyword_class],
        name_type=name_type
    )

def combine_2_words(modword_1_obj: Modword, modword_2_obj: Modword, pos_list: List[str], modifiers: List[str], fit: str = None) -> Name:

    if fit == "fit_":

        name_c2w = "".join(
            [
                modword_1_obj.modword[:-1].title(),
                modword_2_obj.modword.title()
            ]
        )
        name_type = categorize_name(modifiers, pos_list, fit)

    else:
        name_c2w = "".join(
            [
                modword_1_obj.modword.title(),
                modword_2_obj.modword.title()
            ]
        )
        name_type = categorize_name(modifiers, pos_list, fit)
    exempt_contained_words = sorted(set(list(modword_1_obj.contained_words or []) + list(modword_2_obj.contained_words or []) + [modword_1_obj.keyword, modword_2_obj.keyword]))

    return Etymology(
        name_in_title=name_c2w,
        modword_tuple=(modword_1_obj.modword, modword_2_obj.modword),
        keyword_tuple=(modword_1_obj.keyword, modword_2_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        exempt_contained=exempt_contained_words,
        keyword_classes= sorted(set([modword_1_obj.keyword_class, modword_2_obj.keyword_class])),
        name_type=name_type
    )

def combine_3_words(modword_1_obj: Modword, modword_2_obj: Modword, modword_3_obj: Modword, pos_list: List[str], modifiers: List[str], fit: str = None) -> Name:

    if fit == "fit_":
        name_c3w = "".join(
            [
                modword_1_obj.modword.title(),
                modword_2_obj.modword[:-1].title(),
                modword_3_obj.modword.title(),
            ]
        )
        name_type = categorize_name(modifiers, pos_list, fit)
    else:
        name_c3w = "".join(
            [
                modword_1_obj.modword.title(),
                modword_2_obj.modword.title(),
                modword_3_obj.modword.title(),
            ]
        )
        name_type = categorize_name(modifiers, pos_list, fit)
    
    exempt_contained_words = sorted(set(list(modword_1_obj.contained_words or []) + list(modword_2_obj.contained_words or []) + list(modword_3_obj.contained_words or []) + [modword_1_obj.keyword, modword_2_obj.keyword, modword_3_obj.keyword]))

    return Etymology(
        name_in_title=name_c3w,
        modword_tuple=(modword_1_obj.modword, modword_2_obj.modword, modword_3_obj.modword),
        keyword_tuple=(modword_1_obj.keyword, modword_2_obj.keyword, modword_3_obj.keyword),
        pos_tuple=pos_list,
        modifier_tuple=modifiers,
        exempt_contained=exempt_contained_words,
        keyword_classes= sorted(set([modword_1_obj.keyword_class, modword_2_obj.keyword_class, modword_3_obj.keyword_class])),
        name_type=name_type
    )

def create_name_obj(etymology_obj: Etymology, name_dict: dict, eng_dict_words: list):

    name_lower = etymology_obj.name_in_title.lower()
    if name_lower not in name_dict.keys():
        phonetic_grade, phonetic_pattern = grade_phonetic(name_lower)
        implaus_chars_list, end_valid_str = word_plausability(name_lower)
        name_dict[name_lower] = Name(
            name_in_lower=name_lower,
            length=len(name_lower),
            phonetic_pattern=phonetic_pattern,
            phonetic_grade=phonetic_grade,
            implaus_chars=implaus_chars_list,
            end_valid=end_valid_str,
            is_word=is_word(name_lower, eng_dict_words),
            exempt_contained=set(etymology_obj.exempt_contained),
            keyword_classes=etymology_obj.keyword_classes,
            etymologies={etymology_obj}
        )
    else:
        name_dict[name_lower].etymologies.add(etymology_obj)
        name_dict[name_lower].keyword_classes = sorted(set(name_dict[name_lower].keyword_classes + etymology_obj.keyword_classes))
        name_dict[name_lower].exempt_contained.update(etymology_obj.exempt_contained)
    
    return name_dict

def clean_wordlist(wordlist, before_pos=None, after_pos=None):

    cleaned_wordlist = set()
    as_joint_pos = f"{before_pos}<joint>{after_pos}"
    for modword_obj in wordlist:
        if modword_obj is not None:
            as_joint_list = modword_obj.restrictions_as_joint
            before_list = modword_obj.restrictions_before
            after_list = modword_obj.restrictions_after

            if before_pos is None and after_pos is None:
                cleaned_wordlist.add(modword_obj)

            elif before_list is None and after_list is None and as_joint_list is None:
                cleaned_wordlist.add(modword_obj)

            elif before_pos is None and after_pos is not None:
                if after_list is None or after_pos in after_list:
                    cleaned_wordlist.add(modword_obj)

            elif before_pos is not None and after_pos is None:
                if before_list is None or before_pos in before_list:
                    cleaned_wordlist.add(modword_obj)

            elif before_pos is not None and after_pos is not None and as_joint_list is not None:
                if as_joint_pos in as_joint_list:
                    cleaned_wordlist.add(modword_obj)

            elif before_list is not None and after_list is not None:
                if before_pos in before_list and after_pos in after_list:
                    cleaned_wordlist.add(modword_obj)

            elif after_list is not None:
                if after_pos in after_list:
                    cleaned_wordlist.add(modword_obj)

            elif before_list is not None:
                if before_pos in before_list:
                    cleaned_wordlist.add(modword_obj)

    return cleaned_wordlist

def make_names(algorithms: List[Algorithm], wordlist: dict, eng_dict_words: list) -> Dict[str, List[Name]]:
    '''
    Names are now stored in a list in a dictionary where the dictionary keys are the keywords being used.
    ie. name such as "actnow" and "nowact" will be stored in the list under the same key.
    This is to ensure that similar names and their permutations are stored together and the final name list will contain
    the top x number of list from each key.
    This is to make sure that the final generated name list don't contain names that are too similar to each other.
    If the user wants variations/permutations of a specific name, they can call upon the list stored under the specific group of keywords.
    '''
    name_dict: dict[List[Name]] = {}
    valid_pos = ["adjective", "noun", "verb", "adverb"]

    for algorithm in algorithms:
        print(f"Generating names with {algorithm}...")
        algorithm_length = len(algorithm)
        wordlist_1_pos = algorithm.components[0].pos
        wordlist_1_modifier = algorithm.components[0].modifier
        key_1 = f"{wordlist_1_pos}|{wordlist_1_modifier}"
        wordlist1 = wordlist[key_1]
        
        if algorithm_length == 1:
            modlist1 = clean_wordlist(wordlist=wordlist1)
            for modword_1_obj in modlist1:
                etymology_obj = combine_1_word(modword_1_obj)
                name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)

        elif algorithm_length == 2:
            wordlist_2_pos = algorithm.components[1].pos
            wordlist_2_modifier = algorithm.components[1].modifier
            key_2 = f"{wordlist_2_pos}|{wordlist_2_modifier}"
            modlist1 = clean_wordlist(wordlist=wordlist1, after_pos=wordlist_2_pos)
            modlist2 = clean_wordlist(wordlist=wordlist[key_2], before_pos=wordlist_1_pos)
            modword_1_obj: Modword
            modword_2_obj: Modword
            for modword_1_obj in modlist1:
                for modword_2_obj in modlist2:
                    pos_list = (modword_1_obj.pos, modword_2_obj.pos)
                    modifiers = (modword_1_obj.modifier, modword_2_obj.modifier)

                    if modword_1_obj.modword_len >= 3 and modword_2_obj.modword_len >= 3:
                        first_chars = set([modword_1_obj.modword[0], modword_2_obj.modword[0]])
                        second_chars = set([modword_1_obj.modword[1], modword_2_obj.modword[1]])
                        last_chars = set([modword_1_obj.modword[-1], modword_2_obj.modword[-1]])
                    else:
                        first_chars = second_chars = last_chars = []
                    
                    if len(first_chars) == 1 and len(second_chars) == 1 and len(last_chars) == 1:
                        etymology_obj = combine_2_words(modword_1_obj, modword_2_obj, pos_list, modifiers, fit="repeating_")
                        name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)

                    elif (
                        modword_1_obj.modword[-1] == modword_2_obj.modword[0]  
                        and modword_1_obj.modword_len >= 3
                        and modword_2_obj.modword_len >= 3
                        and modword_1_obj.modifier == "no_cut"
                        and modword_2_obj.modifier == "no_cut"
                        and modword_2_obj.pos != "suffix"
                    ):
                        etymology_obj = combine_2_words(modword_1_obj, modword_2_obj, pos_list, modifiers, fit="fit_")
                        name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)
                    elif (
                        modword_1_obj.modword[-1] == modword_2_obj.modword[0]  
                        and modword_1_obj.modword_len >= 4
                        and modword_2_obj.modword_len >= 3
                        and modword_2_obj.modifier == "no_cut"
                        and modword_2_obj.pos != "suffix"
                    ):
                        etymology_obj = combine_2_words(modword_1_obj, modword_2_obj, pos_list, modifiers, fit="fit_")
                        name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)
                    
                    # create non-fit name too
                    etymology_obj = combine_2_words(modword_1_obj, modword_2_obj, pos_list, modifiers)
                    name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)

        elif algorithm_length == 3:
            wordlist_2_pos = algorithm.components[1].pos
            wordlist_2_modifier = algorithm.components[1].modifier
            wordlist_3_pos = algorithm.components[2].pos
            wordlist_3_modifier = algorithm.components[2].modifier
            key_2 = f"{wordlist_2_pos}|{wordlist_2_modifier}"
            key_3 = f"{wordlist_3_pos}|{wordlist_3_modifier}"
            modlist1 = clean_wordlist(wordlist=wordlist1, after_pos=wordlist_2_pos)
            modlist2 = clean_wordlist(wordlist=wordlist[key_2], before_pos=wordlist_1_pos, after_pos=wordlist_3_pos)
            modlist3 = clean_wordlist(wordlist=wordlist[key_3], before_pos=wordlist_2_pos)
            modword_1_obj: Modword
            modword_2_obj: Modword
            modword_3_obj: Modword
            for modword_1_obj in modlist1:
                for modword_2_obj in modlist2:
                    for modword_3_obj in modlist3:
                        pos_list = (modword_1_obj.pos, modword_2_obj.pos, modword_3_obj.pos)
                        modifiers = (modword_1_obj.modifier, modword_2_obj.modifier, modword_3_obj.modifier)
                        if modword_1_obj.modword_len >= 3 and modword_2_obj.modword_len >= 3 and modword_3_obj.modword_len >= 3:
                            first_chars = set([modword_1_obj.modword[0], modword_2_obj.modword[0], modword_3_obj.modword[0]])
                            second_chars = set([modword_1_obj.modword[1], modword_2_obj.modword[1], modword_3_obj.modword[1]])
                            last_chars = set([modword_1_obj.modword[-1], modword_2_obj.modword[-1], modword_3_obj.modword[-1]])
                        else:
                            first_chars = second_chars = last_chars = []
                            
                        if len(first_chars) == 1 and len(second_chars) == 1 and len(last_chars) == 1:
                            etymology_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, pos_list, modifiers, fit="repeating_")
                            name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)

                        elif (
                            modword_2_obj.modword[-1] == modword_3_obj.modword[0] 
                            and modword_1_obj.modword_len >= 3
                            and modword_2_obj.modword_len >= 4
                            and modword_3_obj.modword_len >= 3
                            and modword_3_obj.modifier == "no_cut"
                            and modword_1_obj.modifier == "no_cut"
                            and modword_3_obj.pos != "suffix"
                        ):
                            etymology_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, pos_list, modifiers, fit="fit_")
                            name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)
                        etymology_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, pos_list, modifiers)
                        name_dict = create_name_obj(etymology_obj, name_dict, eng_dict_words)
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
        name_data.exempt_contained = list(name_data.exempt_contained)
        sorted_name_dict[name_in_lower] = name_data

    return sorted_name_dict
