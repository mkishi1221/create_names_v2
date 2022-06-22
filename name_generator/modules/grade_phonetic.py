#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def grade_phonetic(text):

    phonetic_pattern = ""
    vowels = "aeiou"
    middle = "yw"

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
        if pattern != "x":
            prev_letter = letter

    eval_pattern = phonetic_pattern.replace("_", "")

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