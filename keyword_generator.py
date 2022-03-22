#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from classes.keyword import Keyword
import sys
import orjson as json
from modules.process_text_with_spacy import process_text_with_spacy
from modules.get_wordAPI import verify_words_with_wordsAPI
import operator
import pandas as pd
from typing import List
import regex as re


def filter_keywords(keywords: List[Keyword]) -> List[Keyword]:
    """
    Filter approved keywords (approved keywords may be the following):
    - Either a noun, verb, or an adjective
    - Not contain any characters except alphabets
    - Word is at least 3 letters
    """
    approved_pos = ["noun", "verb", "adjective", "adverb"]
    illegal_char = re.compile(r"[^a-zA-Z]")
    approved_keywords = []
    discarded_keywords = []
    
    for keyword in keywords:
        if (
            keyword.pos in approved_pos
            and not bool(illegal_char.search(keyword.keyword))
            and keyword.keyword_len > 2
        ):
            approved_keywords.append(keyword)
        else:
            discarded_keywords.append(keyword)

    discarded_keywords = list(set(discarded_keywords))
    approved_keywords = list(set(approved_keywords))

    with open("ref/illegal_keywords.json", "wb+") as out_file:
        out_file.write(json.dumps(list(set(discarded_keywords)), option=json.OPT_INDENT_2))

    df1 = pd.DataFrame.from_dict(discarded_keywords, orient="columns")
    df1.to_excel("ref/illegal_keywords.xlsx")        

    return list(approved_keywords)

# "text_file" input is a filepath
# "user_keywords_file" input is a filepath
# "output" input is a filepath
def generate_word_list(text_file: str, user_keywords_file: str, output: str):

    all_keywords: List[Keyword] = []

    # Check if keywords exists
    user_keywords = open(user_keywords_file, "r").read().splitlines()
    if len(user_keywords) != 0:

        print("Extracting keywords from keyword list and processing them through spacy......")
        # Spacy is used here as well to generate "lemma" values - this form is more commonly found in wordsAPI dictionary
        user_keywords = sorted(set(user_keywords))
        user_keywords = process_text_with_spacy(user_keywords)
        for keyword in user_keywords:
            keyword.origin = ["keyword_list"]
            keyword.spacy_pos = None
            keyword.pos = None
            keyword.spacy_occurrence = None

        print("Getting keyword pos using wordAPI dictionary......")
        keyword_list_keywords = verify_words_with_wordsAPI(user_keywords)

        with open("ref/keywords_from_keyword-list.json", "wb+") as out_file:
            out_file.write(json.dumps(keyword_list_keywords, option=json.OPT_INDENT_2))

    # Check if sentences exists
    sentences = open(text_file, "r").read().splitlines()
    if len(sentences) != 0:

        # Filter out unique lines from source data containing sentences
        print("Finding unique lines...")
        unique_lines = sorted(set(sentences))

        # Run lines through Spacy to obtain keywords and categorize them according to their POS
        print("Extracting keywords from sentences using spacy...")
        sentence_keywords = process_text_with_spacy(unique_lines)
        for keyword in sentence_keywords:
            keyword.origin = ["sentences"]

        print("Verifying keyword pos using wordAPI dictionary......")
        sentence_keywords = verify_words_with_wordsAPI(sentence_keywords)

        for keyword in sentence_keywords:
            if keyword in keyword_list_keywords:
                keyword.origin.append("keyword_list")
                all_keywords.append(keyword)
            else:
                all_keywords.append(keyword)

        for keyword in keyword_list_keywords:
            if keyword not in all_keywords:
                all_keywords.append(keyword)

        with open("ref/keywords_from_sentences.json", "wb+") as out_file:
            out_file.write(json.dumps(sentence_keywords, option=json.OPT_INDENT_2))

    # Quit if both files are empty
    if sentences == "" and len(user_keywords) == 0:
        print(
            'No sentences and keywords detetcted! Please add source data to the "data" folder.'
        )
        quit()

    # # Run keywords through keywords filter
    print("Running keywords through keyword filter...")
    keywords = filter_keywords(all_keywords)

    print("Sorting keywords and exporting files...")
    keywords.sort(key=operator.attrgetter('keyword'))

    with open("tmp/keywords.json", "wb+") as out_file:
        out_file.write(json.dumps(keywords, option=json.OPT_INDENT_2))

    # Export to excel file
    df1 = pd.DataFrame.from_dict(keywords, orient="columns")
    df1.insert(10, column="Keyword shortlist (insert \"s\")", value="")
    df1.to_excel(output)

if __name__ == "__main__":
    generate_word_list(sys.argv[1], sys.argv[2], sys.argv[3])
