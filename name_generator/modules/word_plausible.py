#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def word_plausability(word):

    end_chars_fp = "name_generator/dict/end_chars.txt"
    end_chars = set(open(end_chars_fp, "r").read().splitlines())
    letter_sets_fp = "../letter_sequences/results/letter_combinations.tsv"
    letter_sets = set(open(letter_sets_fp, "r").read().splitlines())
    length = 4
    letters_list = set()

    for start in range(0,len(word)-length+1):
        end = start + length
        letters_list.add(word[start:end])

    implaus_chars =[]
    for comb in letters_list:
        if comb not in letter_sets:
            implaus_chars.append(comb)

    if word[-2:] not in end_chars:
        valid_end = "not_valid"
    else:
        valid_end = "valid"
    
    return implaus_chars, valid_end


