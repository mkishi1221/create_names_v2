#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def grade_name(name_type, phonetic_grade, implaus_chars, end_valid, is_it_word, name_length, contained_words, if_wiki_title):

    grade_str = None
    reject_reason = None
    approved_phonetic = ["Phonetic_A", "Phonetic_B"]

    if contained_words is not None:
        contained_words = [cw for cw in contained_words if len(cw) > 1]
        if len(contained_words) == 0:
            contained_words = None

    if name_type[:3] == "fit":
        name_type = name_type[4:]
        implaus_chars = []
    elif name_type[:9] == "repeating":
        name_type = name_type[10:]

    if name_type == "cut_name" or name_type == "pref_suff_name":
        if (
            len(implaus_chars) <= 4
            and end_valid == "valid"
            and is_it_word == "no"
            and name_length > 4
            and name_length < 20
            and contained_words == None
            and if_wiki_title == None
            and phonetic_grade in approved_phonetic
        ):
            if phonetic_grade == "Phonetic_A" and len(implaus_chars) <= 1:
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_A" and len(implaus_chars) <= 2:
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_B" and len(implaus_chars) <= 3:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
        else:
            reject_reason = []
            if len(implaus_chars) > 4:
                reject_reason.append("over_4_implausible_chars")
            if end_valid != "valid":
                reject_reason.append("end_invalid")
            if is_it_word != "no":
                reject_reason.append("is_word")
            if name_length <= 4:
                reject_reason.append("under_5_letters")
            if name_length >= 20:
                reject_reason.append("over_20_letters")
            if contained_words != None:
                reject_reason.append("contained_words")
            if if_wiki_title != None:
                reject_reason.append("wiki_title")
            if phonetic_grade not in approved_phonetic:
                reject_reason.append("low phonetic quality")


    elif name_type == "part_cut_name":
        if (
            is_it_word == "no"
            and name_length > 4
            and name_length < 20
            and contained_words == None
            and if_wiki_title == None
            and phonetic_grade in approved_phonetic
        ):
            if phonetic_grade == "Phonetic_A" and len(implaus_chars) <= 1:
                grade_str = "Grade_A"
            elif phonetic_grade == "Phonetic_A" and len(implaus_chars) <= 2:
                grade_str = "Grade_B"
            elif phonetic_grade == "Phonetic_B" and len(implaus_chars) <= 3:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
        else:
            reject_reason = []
            if is_it_word != "no":
                reject_reason.append("is_word")
            if name_length <= 4:
                reject_reason.append("under_5_letters")
            if name_length >= 20:
                reject_reason.append("over_20_letters")
            if contained_words != None:
                reject_reason.append("contained_words")
            if if_wiki_title != None:
                reject_reason.append("wiki_title")
            if phonetic_grade not in approved_phonetic:
                reject_reason.append("low phonetic quality")

    elif name_type == "no_cut_name" or name_type == "text_comp_name" or name_type == "fun_name":
        if (
            is_it_word == "no"
            and name_length > 4
            and name_length < 20
            and contained_words == None
            and if_wiki_title == None
        ):
            if name_length < 11 and phonetic_grade in approved_phonetic:
                grade_str = "Grade_A"
            elif name_length < 13 and phonetic_grade in approved_phonetic:
                grade_str = "Grade_B"
            elif name_length < 17 and phonetic_grade == "Phonetic_C" :
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
        else:
            reject_reason = []
            if is_it_word != "no":
                reject_reason.append("is_word")
            if name_length <= 4:
                reject_reason.append("under_5_letters")
            if name_length >= 20:
                reject_reason.append("over_20_letters")
            if contained_words != None:
                reject_reason.append("contained_words")
            if if_wiki_title != None:
                reject_reason.append("wiki_title")

    return grade_str, reject_reason