#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import copy

def grade_phonetic(text):

    phonetic_pattern = ""
    vowels = "aeiou"
    middle = "yw"
    approved_repeat_strings = ["ss", "ll", "oo", "ee", "tt", "rr", "pp", "nn", "mm", "ff", "gg", "cc", "dd", "bb", "zz"]

    last_index = len(text) - 1
    prev_letter = ""
    for index, letter in enumerate(text):
        if index != last_index and letter == text[index+1]:
            pattern = "_"
        elif letter in vowels:
            pattern = "1"
        elif letter in middle:
            if prev_letter in vowels:
                pattern = "2"
            else:
                pattern = "1"
        else:
            pattern = "2"
        phonetic_pattern = phonetic_pattern + pattern
        prev_letter = letter

    phonetic_pattern_for_eval = copy.deepcopy(phonetic_pattern)

    if "_" in phonetic_pattern_for_eval:
        indexes = [i for i, letter in enumerate(phonetic_pattern_for_eval) if letter == "_"]

        for index in indexes:
            repeat_str = text[index] + text[index+1]
            if repeat_str not in approved_repeat_strings:
                phonetic_pattern_list = list(phonetic_pattern_for_eval)
                phonetic_pattern_list[index] = phonetic_pattern_list[index+1]
                phonetic_pattern_for_eval = "".join(phonetic_pattern_list)

    eval_pattern = phonetic_pattern_for_eval.replace("_", "")

    vowel_count = eval_pattern.count("11")
    consonant_count = eval_pattern.count("22")

    if (
        consonant_count == 0
        and vowel_count == 0
    ):
        phonetic_grade = "Phonetic_A"
    elif (
        consonant_count == 0
        and vowel_count == 1
    ):
        phonetic_grade = "Phonetic_B"
    elif (
        consonant_count <= 1
        and vowel_count <= 1
    ):
        phonetic_grade = "Phonetic_C"

    else:
        phonetic_grade = "Phonetic_D"

    return phonetic_grade, phonetic_pattern
