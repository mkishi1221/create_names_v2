#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from typing import Dict
import regex as re
import copy
import orjson as json
from classes.name_style_class import Name_Style
from classes.name_style_class import Component
from classes.name_class import Etymology
from classes.name_class import Name
from classes.keyword_class import Modword
from modules.generate_phonetic import generate_phonetic
from modules.word_plausible import word_plausability
from modules.generate_hard_lemma import generate_hard_lemma

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

def count_phonetic(phonetic_pattern: str):

    vowel_count = phonetic_pattern.count("11")
    consonant_count = phonetic_pattern.count("22")
    phonetic_values = {"double_vowels":vowel_count, "double_consonants":consonant_count}

    return phonetic_values

def name_length_scorer(name_length: int) -> int:

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

def combine_1_word(modword_1_obj: Modword, name_style: List[Component]) -> Name:
    name_c1w = modword_1_obj.modword.title()
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_style_update = copy.deepcopy(name_style)
    name_style_update[0].keyword = modword_1_obj.keyword
    name_style_update[0].modword = modword_1_obj.modword
    name_keywords = [modword_1_obj.keyword]

    return Etymology(
        name_in_title=name_c1w,
        keywords=name_keywords,
        name_styles=[name_style_update]
    )

def combine_2_words(modword_1_obj: Modword, modword_2_obj: Modword, name_style: List[Component]) -> Name:
    name_c2w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title()
        ]
    )
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_style_update = copy.deepcopy(name_style)
    name_style_update[0].keyword = modword_1_obj.keyword
    name_style_update[0].modword = modword_1_obj.modword
    name_style_update[1].keyword = modword_2_obj.keyword
    name_style_update[1].modword = modword_2_obj.modword
    name_keywords = sorted(set([modword_1_obj.keyword, modword_2_obj.keyword]))

    return Etymology(
        name_in_title=name_c2w,
        keywords=name_keywords,
        name_styles=[name_style_update],
    )

def combine_3_words(modword_1_obj: Modword, modword_2_obj: Modword, modword_3_obj: Modword, name_style: List[Component]) -> Name:
    name_c3w = "".join(
        [
            modword_1_obj.modword.title(),
            modword_2_obj.modword.title(),
            modword_3_obj.modword.title(),
        ]
    )
    # other scores will be added to name_score later (ie. legibility scores etc.)
    name_style_update = copy.deepcopy(name_style)
    name_style_update[0].keyword = modword_1_obj.keyword
    name_style_update[0].modword = modword_1_obj.modword
    name_style_update[1].keyword = modword_2_obj.keyword
    name_style_update[1].modword = modword_2_obj.modword
    name_style_update[2].keyword = modword_3_obj.keyword
    name_style_update[2].modword = modword_3_obj.modword
    name_keywords = sorted(set([modword_1_obj.keyword, modword_2_obj.keyword, modword_3_obj.keyword]))

    return Etymology(
        name_in_title=name_c3w,
        keywords=name_keywords,
        name_styles=[name_style_update],
    )

def create_name_obj(etymology_obj: Etymology, name_dict: dict, wordsAPI_data: dict):

    name_lower = etymology_obj.name_in_title.lower()
    name_title = etymology_obj.name_in_title

    if name_lower not in name_dict.keys():

        name_length = len(name_lower)
        name_length_score = name_length_scorer(name_length)
        phonetic_patt = generate_phonetic(name_lower)
        phonetic_values = count_phonetic(phonetic_patt)
        word_plaus = word_plausability(name_lower)
        is_it_word = is_word(name_lower, wordsAPI_data)
        # other scores will be added to name_score later (ie. legibility scores etc.)
        name_score = int(name_length_score)

        name_dict[name_lower] = Name(
            name_in_lower=name_lower,
            length=name_length,
            length_score=name_length_score,
            total_score=name_score,
            phonetic_pattern=phonetic_patt,
            phonetic_count=phonetic_values,
            word_plausibility=word_plaus,
            is_word=is_it_word,
            etymologies={name_title:etymology_obj}
        )
    else:
        if name_title in name_dict[name_lower].etymologies.keys():
            name_dict[name_lower].etymologies[name_title].name_styles.extend(etymology_obj.name_styles)
            name_dict[name_lower].etymologies[name_title].keywords.extend(etymology_obj.keywords)
            name_dict[name_lower].etymologies[name_title].keywords = sorted(set(name_dict[name_lower].etymologies[name_title].keywords))

        else:
            name_dict[name_lower].etymologies[name_title] = etymology_obj
    
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

def make_names(name_styles: List[Name_Style], wordlist: dict) -> Dict[str, List[Name]]:
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

    main_wordsAPI_dict_fp = "../wordsAPI/original_data/wordsapi_list.json"
    with open(main_wordsAPI_dict_fp) as wordsAPI_file:
        wordsAPI_data = json.loads(wordsAPI_file.read())

    for name_style in name_styles:
        print(f"Generating names with {name_style}...")

        name_style_length = len(name_style)

        wordlist_1_pos = name_style.components[0].keyword_type
        wordlist_1_modifier = name_style.components[0].modifier
        wordlist1 = wordlist[wordlist_1_pos]
        if name_style_length == 1:
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                etymology_obj = combine_1_word(modword_1_obj, name_style.components)
                name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        elif name_style_length == 2:
            wordlist_2_pos = name_style.components[1].keyword_type
            wordlist_2_modifier = name_style.components[1].modifier
            wordlist2 = wordlist[wordlist_2_pos]
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                for keyword_2_obj in wordlist2:
                    modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                    etymology_obj = combine_2_words(modword_1_obj, modword_2_obj, name_style.components)
                    name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        elif name_style_length == 3:
            wordlist_2_pos = name_style.components[1].keyword_type
            wordlist_2_modifier = name_style.components[1].modifier
            wordlist2 = wordlist[wordlist_2_pos]
            wordlist_3_pos = name_style.components[2].keyword_type
            wordlist_3_modifier = name_style.components[2].modifier
            wordlist3 = wordlist[wordlist_3_pos]
            for keyword_1_obj in wordlist1:
                modword_1_obj = keyword_modifier(keyword_1_obj, wordlist_1_modifier)
                for keyword_2_obj in wordlist2:
                    modword_2_obj = keyword_modifier(keyword_2_obj, wordlist_2_modifier)
                    for keyword_3_obj in wordlist3:
                        modword_3_obj = keyword_modifier(keyword_3_obj, wordlist_3_modifier)
                        etymology_obj = combine_3_words(modword_1_obj, modword_2_obj, modword_3_obj, name_style.components)
                        name_dict = create_name_obj(etymology_obj, name_dict, wordsAPI_data)

        else:
            if name_style_length > 3:
                print("Name Style contains more than 3 keywords!")
            elif name_style_length < 1:
                print("Name Style contains no keywords!")

    # Sort name dict by keys.
    name_dict = {key: name_dict[key] for key in sorted(name_dict.keys())}

    return name_dict
