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


def score_phonetic(text: str, xgrams_dict):

    text = text.lower()
    gram_types = ["bigrams", "trigrams", "quadgrams", "pentagrams"]
    score_types = ["startFreq", "gramFreq", "endFreq"]
    breakdown = {}
    implaus_chars = set()
    for length in range(2,6):
        gramtype = gram_types[length-2]
        breakdown[gramtype] = {"startFreq":[], "gramFreq":[], "endFreq":[]}
        if length < len(text):
            for start in range(0,len(text)):
                end = start + length
                gram = text[start:end]
                if end <= len(text):
                    if start == 0:
                        dictRef = "startFreq"
                    elif end == len(text):
                        dictRef = "endFreq"
                    else:
                        dictRef = "gramFreq"
                    try:
                        freq = xgrams_dict[gramtype][gram][dictRef]
                    except KeyError:
                        freq = 0
                        implaus_chars.add(gram)
                    breakdown[gramtype][dictRef].append(freq)

    score_list = []
    average_scores = {}
    for gramtype in gram_types:
        average_scores[gramtype] = {}
        for dictRef in score_types:
            max_freq = xgrams_dict[gramtype]["max_values"]["gramFreq"]
            if len(breakdown[gramtype][dictRef]) > 0:
                try:
                    normalised = sum(breakdown[gramtype][dictRef])/len(breakdown[gramtype][dictRef])/max_freq
                    average_scores[gramtype][dictRef] = normalised
                    score_list.append(normalised)
                except ZeroDivisionError:
                    average_scores[gramtype][dictRef] = 0.0
                    score_list.append(0.0)
    try:
        sorted_scores = sorted(score_list)
        score = sum(sorted_scores)/len(sorted_scores)
        lowest = sum(sorted_scores[:3])/len(sorted_scores[:3])
    except ZeroDivisionError:
        score = 0
        lowest = 0
    implaus_chars = sorted(implaus_chars)
    return score, lowest, implaus_chars