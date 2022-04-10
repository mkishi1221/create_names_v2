#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List
from classes.keyword_class import Keyword
import regex as re
import copy
import orjson as json
import pandas as pd

def filter_keywords(keywords: List[Keyword], discarded_keywords_output_fp) -> List[Keyword]:
    """
    Filter approved keywords (approved keywords may be the following):
    - Either a noun, verb, or an adjective
    - Not contain any characters except alphabets
    - Word is at least 3 letters
    """
    default_blacklist_fp = "dict/default_blacklist.txt"
    blacklist = open(default_blacklist_fp, "r").read().splitlines()
    approved_pos = ["noun", "verb", "adjective", "adverb"]
    illegal_char = re.compile(r"[^a-zA-Z]")
    legal_char = re.compile(r"[a-zA-Z]")
    approved_keywords = []
    discarded_keywords = []
    # discarded_keywords_output_fp = "results/discarded_keywords.json"

    pos_conversion = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJ": "adjective",
    "ADV": "adverb",
    "DET": "definite article",
    "CCONJ": "conjunction",
    "ADP": "adposition",
    "PART": "preposition",
    "PRON": "pronoun"
    }

    for keyword in keywords:

        if keyword.keyword in blacklist:
            keyword = copy.deepcopy(keyword)
            keyword.pos = "Common"
    
        elif keyword.pos is None:
            if keyword.spacy_pos is not None:
                spacy_pos = keyword.spacy_pos

                if spacy_pos in pos_conversion.keys():
                    conv_pos = pos_conversion[spacy_pos]
                    keyword = copy.deepcopy(keyword)
                    keyword.pos = conv_pos            

        if (
            keyword.pos in approved_pos
            and not bool(illegal_char.search(keyword.keyword))
            and keyword.keyword_len > 2
        ):
            approved_keywords.append(keyword)
        elif bool(legal_char.search(keyword.keyword)):
            discarded_keywords.append(keyword)

    discarded_keywords = list(set(discarded_keywords))
    approved_keywords = list(set(approved_keywords))

    with open(discarded_keywords_output_fp, "wb+") as out_file:
        out_file.write(json.dumps(list(set(discarded_keywords)), option=json.OPT_INDENT_2))

    # Excel output for reference only: remove for production
    excel_output = "".join([discarded_keywords_output_fp[:-5], ".xlsx"])
    df1 = pd.DataFrame.from_dict(discarded_keywords, orient="columns")
    df1.to_excel(excel_output)        

    return list(approved_keywords)