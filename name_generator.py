#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
import orjson as json
from modules.combine_words import combine_words
from modules.collect_algorithms import collect_algorithms
from classes.algorithm import Algorithm
import pandas as pd
from classes.keyword import Keyword

def pull_dictionary(dictionary_file, keyword_type):
    df = pd.read_excel(dictionary_file, index_col=0)
    final_df = df[df["Keyword shortlist (insert \"s\")"] == "s"]
    final_df = final_df.fillna('')
    target_list = []
    for index, row in final_df.iterrows():
        target_list.append(
            Keyword(
                origin="dictionary",
                source_word="",
                spacy_lemma="",
                keyword=row["keyword"],
                keyword_len=row["keyword_len"],
                spacy_pos="",
                wordsAPI_pos="",
                pos=keyword_type,
                spacy_occurrence="",
                keyword_user_score=row["keyword_user_score"],
                keyword_wiki_score=row["keyword_wiki_score"],
                keyword_total_score=row["keyword_total_score"],
                pairing_limitations=row["pairing_limitations"]
            )
        )
    return target_list

# Generate name ideas
def generate_names(keyword_file, algorithm_file, output):

    # Access keyword list and sort words into verbs, nouns or adjectives
    df = pd.read_excel(keyword_file, index_col=0)
    keyword_df = df[df["Keyword shortlist (insert \"s\")"] == "s"]
    keyword_df = keyword_df.fillna('')
    verbs = []
    nouns = []
    adjectives = []

    for index, row in keyword_df.iterrows():
        keyword_obj = Keyword(
            origin=row["origin"],
            source_word=row["source_word"],
            spacy_lemma=row["spacy_lemma"],
            keyword=row["keyword"],
            keyword_len=row["keyword_len"],
            spacy_pos=row["spacy_pos"],
            wordsAPI_pos=row["wordsAPI_pos"],
            pos=row["pos"],
            spacy_occurrence=row["spacy_occurrence"],
            keyword_user_score=row["keyword_user_score"],
            keyword_wiki_score=row["keyword_wiki_score"],
            keyword_total_score=row["keyword_total_score"],
            pairing_limitations=row["pairing_limitations"]
        )

        if row["wordsAPI_pos"] == "noun":
            nouns.append(keyword_obj)
        elif row["wordsAPI_pos"] == "verb":
            verbs.append(keyword_obj)
        elif row["wordsAPI_pos"] == "adjective":
            adjectives.append(keyword_obj)

    # Access suffix list and add to suffix list
    prefix_file = "dict/prefix.xlsx"
    keyword_type = "prefix"
    prefixes = pull_dictionary(prefix_file, keyword_type)
    suffix_file = "dict/suffix.xlsx"
    keyword_type = "suffix"
    suffixes = pull_dictionary(suffix_file, keyword_type)

    # these lists will be added later
    joints = []
    determiners = []

    # Add all lists into dict form
    keyword_dict = {
        "verb": verbs,
        "noun": nouns,
        "adje": adjectives,
        "pref": prefixes,
        "suff": suffixes,
        "join": joints,
        "detr": determiners
    }

    with open("tmp/keyword_shortlist.json", "wb+") as out_file:
        out_file.write(json.dumps(keyword_dict, option=json.OPT_INDENT_2))

    # Get all algorithms
    algorithms = collect_algorithms(algorithm_file)

    # Generate names by combining two keywords together
    def combine(alg: Algorithm):
        print(
            f"Generating names with {alg}..."
        )

        return combine_words(
            alg,
            keyword_dict,
        )

    all_names = [name for alg in algorithms for name in combine(alg)]
    all_names = sorted(all_names, key=lambda k: (k.score * -1, k.name))

    with open(sys.argv[3], "wb+") as out_file:
        # remove below indent when no further debug needed for more speeeeeed
        out_file.write(json.dumps(all_names, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))


if __name__ == "__main__":
    generate_names(sys.argv[1], sys.argv[2], sys.argv[3])
