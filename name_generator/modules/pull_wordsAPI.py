#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json

def pull_wordsAPI_dict():

    main_wordsAPI_dict_fp = "../wordsAPI/cleaned_wordAPI_dict.json"
    with open(main_wordsAPI_dict_fp) as wordsAPI_file:
        wordsAPI_data = json.loads(wordsAPI_file.read())

    return wordsAPI_data