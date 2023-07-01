#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re

def create_keyword(word_str: str, keyword_str: str) -> Keyword:

    return Keyword(
        source_words=[word_str],
        keyword=keyword_str,
        keyword_len=len(keyword_str),
        origin = ["keyword_list"]
    )

def process_keyword_list(user_keywords: List[str]) -> List[Keyword]:
    print("Extracting keywords from keyword list...")
    keywords: dict[Keyword] = {}
    for raw_keyword in user_keywords:
        not_valid = [None, ""]
        if raw_keyword not in not_valid:
            word_str = raw_keyword.strip()
            keyword_str = re.sub(r"^\W+", "", raw_keyword).lower()
            keyword_str = re.sub(r"\W+$", "", keyword_str)
            kw_obj = create_keyword(word_str, keyword_str)
            if keyword_str not in keywords.keys():
                keywords[keyword_str] = kw_obj
            else:
                source_word_list = sorted(set(keywords[keyword_str].source_words + [word_str]))
                keywords[keyword_str].source_words = source_word_list

    # Sort keyword list according to:
    # 1. "keyword" in alphabetical order
    # 2. "original" word in alphabetical order.
    sorted_keywords = sorted(
        list(keywords.values()), key=lambda k: (k.keyword)
    )

    return sorted_keywords
