#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def grade_phonetic(text):

    phonetic_pattern = []

    vowels = "aeiou"
    middle = "yw"
    numbers = "12"

    prev_letter = ""
    for letter in text:
        if letter in numbers:
            phonetic_pattern.append(letter)
        elif letter in vowels:
            phonetic_pattern.append("1")
        elif letter in middle:
            if prev_letter in vowels:
                phonetic_pattern.append("2")
            else:
                phonetic_pattern.append("1")
        else:
            phonetic_pattern.append("2")
        prev_letter = letter
    
    phonetic_pattern = "".join(phonetic_pattern)

    vowel_count = phonetic_pattern.count("11")
    consonant_count = phonetic_pattern.count("22")

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


    return phonetic_grade