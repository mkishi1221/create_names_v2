#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword import Keyword
import regex as re
import spacy


nlp = spacy.load("en_core_web_lg")


def create_keyword(word: str, word_pos: str, word_lemma: str) -> Keyword:
    """
    summary:
        Creates a "keyword" so that similar words are grouped together regardless of their case-styles/symbols used.
        Removes non-alphabet characters from beginning and end of word and saves it as lowercase "keyword".
        (eg. "+High-tech!" → "high-tech" )
    parameters:
        word: str; word to create keyword from
        word_pos: str; Coarse-grained part-of-speech from the Universal POS tag set. (eg. noun, verb etc.)
        word_tag: str; Fine-grained part-of-speech. (eg. NN = singular noun, NNS = plural noun etc.)
        word_dep: str; Syntactic dependency relation. (What relations the word has to other words in the sentence.)
        word_lemma: str; Base form of the token, with no inflectional suffixes. (eg. word = changing, lemma = change)
    returns:
        token_dict: dict; a dictionary containing all important parameters of keyword
    """
    processed_word = re.sub(r"^\W+", "", word).lower()
    processed_word = re.sub(r"\W+$", "", processed_word)

    return Keyword(
        source_word=word,
        spacy_lemma=word_lemma,
        keyword=processed_word,
        keyword_len=len(processed_word),
        spacy_pos=word_pos
    )


def process_text_with_spacy(lines: list[str]) -> List[Keyword]:
    keywords: list[Keyword] = []
    for line in lines:
        doc = nlp(line)

        # Spacy divides sentences ("sent") into words ("tokens").
        # Tokens can also be symbols and other things that are not full words.
        for sent in doc.sents:
            for token in sent:
                word = token.text
                word_pos = token.pos_
                word_lemma = token.lemma_

                keywords.append(create_keyword(word, word_pos, word_lemma))

    unique_words = []
    for keyword in keywords:
        if keyword.source_word != "" and keyword.keyword_len >= 1 and keyword not in unique_words:
            unique_words.append(keyword)

    # Count occurrence of unique word
    for unique_word in unique_words:
        unique_word.spacy_occurrence = keywords.count(unique_word)

    # Sort keyword list according to:
    # 1. "keyword" in alphabetical order
    # 2. occurrence
    # 3. "original" word in alphabetical order.
    sorted_unique_words = sorted(
        unique_words, key=lambda k: (k.keyword, -k.spacy_occurrence, k.source_word.lower())
    )

    return sorted_unique_words
