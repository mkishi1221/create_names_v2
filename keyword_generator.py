#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from modules.get_keyword_wiki_scores import get_keyword_wiki_scores
from classes.keyword import Keyword
import sys
import orjson as json
from modules.find_unique_lines import find_unique_lines
from modules.extract_words_with_spacy import extract_words_with_spacy
from modules.import_keyword_list import import_keyword_list
from modules.get_wordAPI import verify_words_with_wordsAPI
from modules.filter_keywords import filter_keywords
import operator


def generate_word_list(text_file, user_keywords_file):

    all_keywords: list[Keyword] = []

    # Check if keywords exists
    user_keywords = open(user_keywords_file, "r").read().splitlines()
    if len(user_keywords) != 0:

        # Get keywords from user keyword list
        print("Extracting keywords from keyword list and verifying keywords using wordAPI dictionary......")
        keyword_list_keywords = import_keyword_list(user_keywords)
        keyword_list_keywords = verify_words_with_wordsAPI(keyword_list_keywords)
        keyword_list_keywords = get_keyword_wiki_scores(keyword_list_keywords)
        all_keywords += keyword_list_keywords
        with open("ref/keywords_from_keyword-list.json", "wb+") as out_file:
            out_file.write(json.dumps(keyword_list_keywords, option=json.OPT_INDENT_2))

    # Check if sentences exists
    sentences = open(text_file, "r").read()
    if sentences != "":

        # Filter out unique lines from source data containing sentences
        print("Finding unique lines...")
        unique_lines = find_unique_lines(sentences)

        # Run lines through Spacy to obtain keywords and categorize them according to their POS
        print("Extracting keywords from sentences using spacy...")
        spacy_keywords = extract_words_with_spacy(unique_lines)
        spacy_keywords = verify_words_with_wordsAPI(spacy_keywords)
        spacy_keywords = get_keyword_wiki_scores(spacy_keywords)

        all_keywords += spacy_keywords
        with open("ref/keywords_from_sentences_.json", "wb+") as out_file:
            out_file.write(json.dumps(spacy_keywords, option=json.OPT_INDENT_2))
    else:
        spacy_keywords = []

    # Quit if both files are empty
    if sentences == "" and len(user_keywords) == 0:
        print(
            'No sentences and keywords detetcted! Please add source data to the "data" folder.'
        )
        quit()

    # Run keywords through keywords filter
    print("Running keywords through keyword filter...")
    keywords = filter_keywords(all_keywords)

    keywords.sort(key=operator.attrgetter('keyword'))
    keywords.sort(key=operator.attrgetter('keyword_total_score'), reverse=True)

    with open(sys.argv[3], "wb+") as out_file:
        out_file.write(json.dumps(keywords, option=json.OPT_INDENT_2))

if __name__ == "__main__":
    generate_word_list(sys.argv[1], sys.argv[2])
