#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword import Keyword
import regex as re
import orjson as json


def create_keyword(word: str) -> Keyword:
    """
    summary:
        Creates a "keyword" so that similar words are grouped together regardless of their case-styles/symbols used.
        Removes non-alphabet characters from beginning and end of word and saves it as lowercase "keyword".
        (eg. "+High-tech!" → "high-tech" )
    """
    processed_word = re.sub(r"^\W+", "", word).lower()
    processed_word = re.sub(r"\W+$", "", processed_word)
    return Keyword(
        origin="keyword_list",
        source_word=word,
        keyword=processed_word,
        keyword_len=len(processed_word),
        keyword_user_score=3,
        keyword_total_score=3
    )


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
        unique_words, key=lambda k: (k.keyword, k.source_word.lower())
    )

    with open("ref/sorted_unique_words.json", "wb+") as out_file:
        out_file.write(json.dumps(sorted_unique_words, option=json.OPT_INDENT_2))

    return sorted_unique_words
