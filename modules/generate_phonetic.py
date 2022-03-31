#!/usr/bin/env python3
# -*- coding:utf-8 -*-

def generate_phonetic(name):

    phonetic_pattern = []

    vowels = "aeiou"
    middle = "yw"
    numbers = "12"

    prev_letter = ""
    for letter in name:
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

    return phonetic_pattern