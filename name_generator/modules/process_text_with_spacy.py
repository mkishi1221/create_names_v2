#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
import regex as re
import spacy

nlp = spacy.load(
    "en_core_web_lg",
    exclude=[
        "ner",
        "entity_linker",
        "entity_ruler",
        "textcat",
        "textcat_multilabel",
        "morphologizer",
        "senter",
        "sentencizer",
        "transformer",
    ],
)

def create_keyword(word: str, word_pos: str, word_lemma: str, processed_word: str) -> Keyword:
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

    return Keyword(
        source_words=[word],
        spacy_lemma=word_lemma,
        keyword=processed_word,
        keyword_len=len(processed_word),
        spacy_pos=word_pos,
        spacy_occurrence = 1
    )

def process_text_with_spacy(lines: List[str]) -> List[Keyword]:
    print("Extracting keywords from sentences using spacy...")
    not_valid = [None, ""]
    keywords: dict[Keyword] = {}
    for line in lines:
        doc = nlp(line)

        # Spacy divides sentences ("sent") into words ("tokens").
        # Tokens can also be symbols and other things that are not full words.
        for sent in doc.sents:
            for token in sent:
                word = token.text.strip()
                processed_word = re.sub(r"^\W+", "", word).lower()
                processed_word = re.sub(r"\W+$", "", processed_word)
                if processed_word not in not_valid:
                    word_pos = token.pos_
                    word_lemma = token.lemma_
                    kw_obj = create_keyword(word, word_pos, word_lemma, processed_word)
                    if word not in keywords.keys():
                        keywords[processed_word] = kw_obj
                    else:
                        source_word_list = sorted(set(keywords[processed_word].source_words + [word]))
                        keywords[processed_word].source_words = source_word_list
                        keywords[processed_word].spacy_occurrence = keywords[processed_word].spacy_occurrence + 1

    # Sort keyword list to "keyword" in alphabetical order
    sorted_unique_words = sorted(
        list(keywords.values()), key=lambda k: (k.keyword)
    )

    return sorted_unique_words
