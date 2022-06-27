#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def grade_name(name_type, phonetic_grade, implaus_chars, is_it_word, name_length, contained_words, if_wiki_title):

    grade_str = None
    if_fit = None

    if name_type[:3] == "fit":
        name_type = name_type[4:]
        implaus_chars = 0
    elif name_type[:9] == "repeating":
        name_type = name_type[10:]

    if name_type == "cut_name":
        if (
            implaus_chars <= 4
            and is_it_word == "no"
            and name_length > 4
            and name_length < 11
            and contained_words == None
            and if_wiki_title == None
        ):
            if phonetic_grade == "Phonetic_A" and implaus_chars == 0:
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_B" and implaus_chars <= 1:
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_C" and implaus_chars <= 2:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
    
    elif name_type == "pref_suff_name":
        if (
            implaus_chars <= 4
            and is_it_word == "no"
            and name_length > 4
            and name_length < 11
            and contained_words == None
            and if_wiki_title == None
        ):
            if phonetic_grade == "Phonetic_A":
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_B":
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_C":
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"

    elif name_type == "no_cut_name" or name_type == "text_comp_name":

        if (
            implaus_chars <= 4
            and is_it_word == "no"
            and name_length > 4
            and contained_words == None
            and if_wiki_title == None
        ):
            if name_length < 11:
                grade_str = "Grade_A"
            elif name_length < 13:
                grade_str = "Grade_B"
            elif name_length < 17:
                grade_str = "Grade_C"
            elif name_length < 20:
                grade_str = "Grade_D"

    return grade_str