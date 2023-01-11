#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json

def pull_eng_dict():

    eng_dict_fp = "../wordsAPI/simplified_eng_dict.json"
    with open(eng_dict_fp) as eng_dict_file:
        eng_dict_data = json.loads(eng_dict_file.read())

    return eng_dict_data