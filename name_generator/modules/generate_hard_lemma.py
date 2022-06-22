#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json

def generate_hard_lemma(keyword: str, data: str=None) -> dict:

    if data == None:
        hard_lemma_conversion_dict_fp = "name_generator/dict/hard_lemma_conversions.json"
    else:
        hard_lemma_conversion_dict_fp = "name_generator/dict/hard_lemma_conversions_short.json"

    with open(hard_lemma_conversion_dict_fp) as hard_lemma_conversion_dict_file:
        hl_conversion_dict = json.loads(hard_lemma_conversion_dict_file.read())

    hard_lemma_1 = None
    hard_lemma_2 = None
    possible_pos = []

    try:
        ending_1 = keyword[-1]
        ending_2 = keyword[-2:]
        ending_3 = keyword[-3:]
        word_cut_1 = keyword[:-1]
        word_cut_2 = keyword[:-2]
        word_cut_3 = keyword[:-3]
    except IndexError:
        print("IndexError: string index out of range")
        print(f"keyword is: {keyword}")
        exit()

    if ending_3 in hl_conversion_dict.keys():
        replacement_1 = hl_conversion_dict[ending_3]["replacement_1"]
        hard_lemma_1 = "".join([word_cut_3, replacement_1])
        if hl_conversion_dict[ending_3]["replacement_2"] is not None:
            replacement_2 = hl_conversion_dict[ending_3]["replacement_2"]
            hard_lemma_2 = "".join([word_cut_3, replacement_2])
        possible_pos.extend(hl_conversion_dict[ending_3]["possible_pos"])

    elif ending_2 in hl_conversion_dict.keys():
        replacement_1 = hl_conversion_dict[ending_2]["replacement_1"]
        hard_lemma_1 = "".join([word_cut_2, replacement_1])
        if hl_conversion_dict[ending_2]["replacement_2"] is not None:
            replacement_2 = hl_conversion_dict[ending_2]["replacement_2"]
            hard_lemma_2 = "".join([word_cut_2, replacement_2])
        possible_pos.extend(hl_conversion_dict[ending_2]["possible_pos"])

    elif ending_1 in hl_conversion_dict.keys():
        replacement_1 = hl_conversion_dict[ending_1]["replacement_1"]
        hard_lemma_1 = "".join([word_cut_1, replacement_1])
        if hl_conversion_dict[ending_1]["replacement_2"] is not None:
            replacement_2 = hl_conversion_dict[ending_1]["replacement_2"]
            hard_lemma_2 = "".join([word_cut_1, replacement_2])
        possible_pos.extend(hl_conversion_dict[ending_1]["possible_pos"])

    if hard_lemma_1 == None and hard_lemma_2 == None:
        hard_lemma_combined = None
    else:
        hard_lemma_combined = {"hard_lemma_1":hard_lemma_1, "hard_lemma_2":hard_lemma_2, "possible_pos":possible_pos}

    return hard_lemma_combined

    