#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword import Keyword
import regex as re


def create_keyword(word: str) -> Keyword:
    """
    summary:
        Creates a "keyword" so that similar words are grouped together regardless of their case-styles/symbols used.
        Removes non-alphabet characters from beginning and end of word and saves it as lowercase "keyword".
        (eg. "+High-tech!" → "high-tech" )
    """
    keyword = re.sub(r"^\W+", "", word)
    keyword = re.sub(r"\W+$", "", keyword)
    return Keyword(word, len(keyword), keyword.lower(), "keyword_list", keyword_user_score=3, keyword_total_score=3)


def import_keyword_list(words) -> List[Keyword]:

    # Create set of unique words
    unique_words = []
    for word in words:
        if len(word) >= 1:
            word = create_keyword(word)
            if word not in unique_words:
                unique_words.append(word)

    # Sort keyword list according to:
    # - "keyword" in alphabetical order
    # - "original" word in alphabetical order.
    sorted_unique_words = sorted(
        unique_words, key=lambda k: (k.keyword, k.word.lower())
    )

    return sorted_unique_words
