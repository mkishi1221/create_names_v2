#!/usr/bin/env python3
# -*- coding:utf-8 -*-
def word_plausability(word):

    letter_sets_fp = "../letter_sequences/results/letter_combinations.tsv"
    letter_sets = set(open(letter_sets_fp, "r").read().splitlines())
    length = 4
    letters_list = set()

    for start in range(0,len(word)-length+1):
        end = start + length
        letters_list.add(word[start:end])

    plausable = None
    for comb in letters_list:
        if comb in letter_sets:
            plausable = "yes"
        elif comb not in letter_sets:
            plausable = "no"
            break
    
    return plausable


