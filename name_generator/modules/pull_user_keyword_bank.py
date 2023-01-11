#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from modules.convert_excel_to_json import convert_excel_to_json
from classes.keyword_class import Preferred_Keyword
import os.path
import orjson as json

def convert_to_list(string: str):
    if len(str(string or "")) > 0:
        str_list = string.replace('[', '').replace(']', '').replace('\"', '').replace(' ', '').replace('\'', '').split(",")
    else:
        str_list = None
    return str_list

def pull_user_keyword_bank(project_path):

    user_keyword_bank_list = []
    user_keyword_bank_fp = f"{project_path}/data/user_keyword_bank.xlsx"
    if os.path.exists(user_keyword_bank_fp):
        user_keyword_bank_json_fp = convert_excel_to_json(user_keyword_bank_fp, target_sheet='user_keyword_bank', output_json_fp=f"{project_path}/tmp/logs/user_keyword_bank.json", convert_list=True)
        with open(user_keyword_bank_json_fp) as user_keyword_bank_file:
            raw_user_keyword_bank_list = json.loads(user_keyword_bank_file.read())
        for kw_obj in raw_user_keyword_bank_list:
            not_valid = [None, ""]
            if kw_obj["keyword"] not in not_valid:
                pos_list = convert_to_list(kw_obj["preferred_pos"])
                origin_list =  convert_to_list(kw_obj["origin"])
                user_keyword_bank_list.append(Preferred_Keyword(keyword=kw_obj["keyword"], preferred_pos=pos_list, origin=origin_list, disable=kw_obj["disable"]))

    return user_keyword_bank_list