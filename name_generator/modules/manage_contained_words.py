#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from modules.convert_excel_to_json import convert_excel_to_json
from modules.pull_eng_dict import pull_eng_dict
import pandas as pd
import orjson as json
import os



def pull_master_exempt():

    master_exempt_cw_txt_fp = "name_generator/master_exempt_contained_words.txt"
    if os.path.exists(master_exempt_cw_txt_fp):
        master_exempt_contained_words = set(open(master_exempt_cw_txt_fp, "r").read().splitlines())
    else:
        master_exempt_contained_words = set()
    master_exempt_cw_xlsx_fp = "name_generator/contained_words.xlsx"
    sheet_name = "contained_words"
    new_exempt_words = set()
    if os.path.exists(master_exempt_cw_xlsx_fp):
        master_exempt_cw_json_fp = convert_excel_to_json(master_exempt_cw_xlsx_fp, sheet_name, convert_list=True)
        with open(master_exempt_cw_json_fp) as master_exempt_cw_file:
            master_exempt_cw_list = json.loads(master_exempt_cw_file.read())
        master_exempt_cw_dict = {}
        for data in master_exempt_cw_list:
            word = data["word"]
            if data["exempt"] not in [None, ""]:
                master_exempt_contained_words.add(word)
                new_exempt_words.add(word)
            else:
                word = data["word"]
                master_exempt_cw_dict[word] = data
        master_exempt_contained_words = sorted(sorted(master_exempt_contained_words), key=len)
        f = open(master_exempt_cw_txt_fp, "w")
        f.write("\n".join(master_exempt_contained_words))
        f.close()
        with open(master_exempt_cw_json_fp, "wb+") as out_file:
            out_file.write(json.dumps(master_exempt_cw_dict, option=json.OPT_SERIALIZE_DATACLASS | json.OPT_INDENT_2))

    curated_eng_word_list_fp = "name_generator/curated_eng_word_list.txt"
    if os.path.exists(curated_eng_word_list_fp):
        curated_eng_word_list = set(open(curated_eng_word_list_fp, "r").read().splitlines())
        for kw in new_exempt_words:
            try:
                curated_eng_word_list.remove(kw)
            except ValueError:
                pass
    else:
        eng_dict:dict = pull_eng_dict()
        curated_eng_word_list: list = list(eng_dict.keys())
        for kw in master_exempt_contained_words:
            try:
                curated_eng_word_list.remove(kw)
            except ValueError:
                pass
    
    f = open(curated_eng_word_list_fp, "w")
    f.write("\n".join(curated_eng_word_list))
    f.close()

    return master_exempt_contained_words

def collect_contained_words(data, master_cw_dict, eng_dict, master_exempt_contained_words):
    contained_words = data.contained_words
    if contained_words is not None:
        for cw in contained_words:
            if cw not in master_exempt_contained_words:
                cw_len = len(cw)
                try:
                    cw_pos = eng_dict[cw]["pos_list"]
                except KeyError:
                    cw_pos = None
                try:
                    freq = eng_dict[cw]["cube_frequency"]
                except KeyError:
                    freq = 0
                if freq is None:
                    freq = 0
                
                if cw is not None and cw != "" and cw not in master_cw_dict.keys():
                    master_cw_dict[cw] = {"word": str(cw), "len": cw_len, "pos_list": cw_pos, "frequency": freq, "count": 1, "exempt": ""}
                else:
                    count = master_cw_dict[cw]["count"] + 1
                    is_exempt = master_cw_dict[cw]["exempt"]
                    master_cw_dict[cw] = {"word": str(cw), "len": cw_len, "pos_list": cw_pos, "frequency": freq, "count": count, "exempt": is_exempt}
    return master_cw_dict


def push_contained_words_list(data_dict: dict, master_exempt_contained_words):

    master_cw_dict = {}

    eng_dict = pull_eng_dict()

    # Sort graded names according to grade and add to contained words dict.
    for key_1, data_1 in data_dict.items():
        if type(data_1) == dict:
            data_1: dict
            for key_2, data_2 in data_1.items():
                master_cw_dict = collect_contained_words(data_2, master_cw_dict, eng_dict, master_exempt_contained_words)
        else:
            master_cw_dict = collect_contained_words(data_1, master_cw_dict, eng_dict, master_exempt_contained_words)

    # sort and export contained words data
    sorted_master_cw_list = sorted(master_cw_dict, key=lambda k: (master_cw_dict[k]["frequency"], master_cw_dict[k]["len"], -master_cw_dict[k]["count"], master_cw_dict[k]["word"]))
    sorted_master_cw_dict = {}
    for cw in sorted_master_cw_list:
        sorted_master_cw_dict[cw] = master_cw_dict[cw]
    if len(sorted_master_cw_dict.keys()) > 0:
        master_cw_list = []
        for word, data in sorted_master_cw_dict.items():
            master_cw_list.append(data)
        df1 = pd.DataFrame.from_dict(master_cw_list, orient="columns")
        writer = pd.ExcelWriter("name_generator/contained_words.xlsx", engine='xlsxwriter')
        df1.to_excel(writer, sheet_name="contained_words")
        workbook  = writer.book
        worksheet = writer.sheets["contained_words"]
        worksheet.set_column(1, 4, 15)
        writer.save()