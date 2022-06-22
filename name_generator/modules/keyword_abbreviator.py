#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def keyword_abbreviator(keyword: str, phonetic_pattern: str):
    
    consonant_count = 0
    vowel_count = 0
    illegal_len = [1, len(keyword)]
    prev_pattern = ""
    modword_str_list = None

    if len(keyword) > 3:
        modword_str_list = []
        for index, pattern in enumerate(phonetic_pattern):
            # 1 represents a vowel character and "2" represents a consonant character.
            if pattern == "1" and pattern != prev_pattern:
                vowel_count = vowel_count + 1
                modword_str = keyword[:index+1]
                if len(modword_str) not in illegal_len:
                    modword_str_list.append(modword_str)
            elif pattern == "2" and pattern != prev_pattern:
                consonant_count = consonant_count + 1
                modword_str = keyword[:index+1]
                if len(modword_str) not in illegal_len:
                    modword_str_list.append(modword_str)
            prev_pattern = pattern

    return modword_str_list