#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def grade_name(name_type, is_it_word, name_length, contained_words, if_wiki_title, lowest, translated):

    grade_str = None
    reject_reason = None

    if contained_words is not None:
        contained_words = [cw for cw in contained_words if len(cw) > 1]
        if len(contained_words) == 0:
            contained_words = None

    if name_type[:3] == "fit":
        name_type = name_type[4:]
    elif name_type[:9] == "repeating":
        name_type = name_type[10:]

    valid_types = ["cut_name", "pref_suff_name", "part_cut_name", "mspl_name"]
    if name_type in valid_types:
        if (
            lowest < 0.7
            and is_it_word == "no"
            and name_length > 4
            and name_length < 20
            and contained_words == None
            and if_wiki_title == None
        ):
            if name_length < 8:
                grade_str = "Grade_A"
            elif name_length < 11:
                grade_str = "Grade_B"
            elif name_length < 14:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
        else:
            grade_str = "Reject"
            reject_reason = []
            if lowest > 0.7:
                reject_reason.append("implausible_chars")
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

    else:
        if translated == "no":
            lowest = 0

        if (
            lowest < 0.7
            and is_it_word == "no"
            and name_length > 4
            and name_length < 20
            and contained_words == None
            and if_wiki_title == None
        ):
            if name_length < 11:
                grade_str = "Grade_A"
            elif name_length < 13:
                grade_str = "Grade_B"
            elif name_length < 17:
                grade_str = "Grade_C"
            else:
                grade_str = "Grade_D"
        else:
            grade_str = "Reject"
            reject_reason = []
            if lowest > 0.7:
                reject_reason.append("implausible_chars")
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