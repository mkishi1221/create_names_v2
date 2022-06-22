#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
from classes.keyword_class import Keyword
from classes.keyword_class import Preferred_Keyword
import regex as re
import pandas as pd
from modules.pull_user_keyword_bank import pull_user_keyword_bank

def convert_to_list(string: str):
    if len(str(string or "")) > 0:
        str_list = string.replace('[', '').replace(']', '').replace('\"', '').replace(' ', '').replace('\'', '').split(",")
    else:
        str_list = None
    return str_list

def create_keyword(word_str: str, keyword_str: str, pos_str_list: list, shortlist_str: str = None) -> Keyword:

    return Keyword(
        source_word=word_str,
        keyword=keyword_str,
        keyword_len=len(keyword_str),
        preferred_pos=pos_str_list,
        shortlist=shortlist_str,
    )

def export_user_keyword_bank(user_keyword_bank_list, project_path):
    # Export User Keyword Bank
    if len(user_keyword_bank_list) > 0:
        user_keyword_bank_list = sorted(user_keyword_bank_list, key=lambda d: (d.keyword, d.preferred_pos))
        df1 = pd.DataFrame.from_dict(user_keyword_bank_list, orient="columns")
        user_keyword_bank_fp = f"{project_path}/data/user_keyword_bank.xlsx"
        writer = pd.ExcelWriter(user_keyword_bank_fp, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='user_keyword_bank')
        workbook  = writer.book
        worksheet = writer.sheets['user_keyword_bank']
        worksheet.set_column(1, 4, 15)
        writer.save()


def process_user_keywords_str(user_keywords: List[str], project_path) -> List[Keyword]:
    user_keyword_bank_list: list[Preferred_Keyword]
    user_keyword_bank_list = pull_user_keyword_bank(project_path)
    keywords: List[Keyword] = []
    for raw_keyword in user_keywords:
        not_valid = [None, ""]
        if raw_keyword not in not_valid:
            keyword_and_pos = [x.strip() for x in raw_keyword.split(',')]
            word_str = keyword_and_pos[0]
            keyword_str = re.sub(r"^\W+", "", word_str).lower()
            keyword_str = re.sub(r"\W+$", "", keyword_str)
            if len(keyword_and_pos) > 1:
                pos_str_list = keyword_and_pos[1:]
                preferred_keyword = Preferred_Keyword(keyword=keyword_str, preferred_pos=pos_str_list, origin=["keyword_list"])
                if preferred_keyword not in user_keyword_bank_list:
                    user_keyword_bank_list.append(preferred_keyword)
                else:
                    kw_index = user_keyword_bank_list.index(preferred_keyword)
                    user_keyword_bank_list[kw_index].preferred_pos.extend(pos_str_list)
                    user_keyword_bank_list[kw_index].preferred_pos = sorted(set(user_keyword_bank_list[kw_index].preferred_pos))

            elif len(keyword_and_pos) == 1:
                pos_str_list = None
        
            else:
                print(f"Invalid user keyword format: \"{raw_keyword}\" Skipping keyword...")
                continue
            keywords.append(create_keyword(word_str, keyword_str, pos_str_list))

    unique_words = []
    for keyword_obj in keywords:
        not_valid = [None, ""]
        if keyword_obj.keyword not in not_valid and keyword_obj not in unique_words:
            unique_words.append(keyword_obj)

    # Sort keyword list according to:
    # 1. "keyword" in alphabetical order
    # 2. "original" word in alphabetical order.
    sorted_unique_words = sorted(
        unique_words, key=lambda k: (k.keyword, k.source_word.lower())
    )

    # Export User Keyword Bank
    export_user_keyword_bank(user_keyword_bank_list, project_path)  

    return sorted_unique_words

def process_user_keywords_dict(user_keywords: List[dict], project_path) -> List[Keyword]:

    user_keyword_bank_list: list[Preferred_Keyword]
    user_keyword_bank_list = pull_user_keyword_bank(project_path)
    keywords: List[Keyword] = []
    keyword_obj: dict
    for keyword_obj in user_keywords:
        word_str = keyword_obj["keyword"]
        keyword_str = re.sub(r"^\W+", "", word_str).lower()
        keyword_str = re.sub(r"\W+$", "", keyword_str)
        not_valid = [None, "", []]
        if keyword_obj["keyword"] not in not_valid:
            if keyword_obj["preferred_pos"] not in not_valid:
                pos_str_list = convert_to_list(keyword_obj["preferred_pos"])
                preferred_keyword = Preferred_Keyword(keyword=keyword_str, preferred_pos=pos_str_list, origin=["additional_keywords"])
                if preferred_keyword not in user_keyword_bank_list:
                    user_keyword_bank_list.append(preferred_keyword)
                else:
                    kw_index = user_keyword_bank_list.index(preferred_keyword)
                    user_keyword_bank_list[kw_index].preferred_pos.extend(pos_str_list)
                    user_keyword_bank_list[kw_index].preferred_pos = sorted(set(user_keyword_bank_list[kw_index].preferred_pos))
                    user_keyword_bank_list[kw_index].origin.append("additional_keywords")
                    user_keyword_bank_list[kw_index].origin = sorted(set(user_keyword_bank_list[kw_index].origin))
            else:
                pos_str_list = None
        else:
            print(f"Invalid user keyword format: \"{keyword_obj.__dict__}\" Skipping keyword...")
            continue
        keywords.append(create_keyword(word_str, keyword_str, pos_str_list, shortlist_str="s"))

    unique_words = []
    for keyword_obj in keywords:
        not_valid = [None, ""]
        if keyword_obj.keyword not in not_valid and keyword_obj not in unique_words:
            unique_words.append(keyword_obj)

    # Sort keyword list according to:
    # 1. "keyword" in alphabetical order
    # 2. "original" word in alphabetical order.
    sorted_unique_words = sorted(
        unique_words, key=lambda k: (k.keyword, k.source_word.lower())
    )

    # Export User Keyword Bank
    export_user_keyword_bank(user_keyword_bank_list, project_path)  

    return sorted_unique_words
