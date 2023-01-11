#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import orjson as json
import pandas as pd

data_fp = "test_keyword_dict.json"
with open(data_fp) as data_file:
    data: dict = json.loads(data_file.read())

keyword_dict = []
required = ["noun", "plrn", "verb", "adje", "advb"]
for key in data.keys():
    if key[:4] in required:
        for keyword_obj in data[key]:
            desired_order_list = [
                "origin",
                "source_word",
                "spacy_pos",
                "eng_dict_pos",
                "keyword_len",
                "contained_words",
                "phonetic_grade",
                "yake_rank",
                "modifier",
                "modword_len",
                "pos",
                "keyword",
                "modword",
                "shortlist",
            ]
            reordered_keyword_obj = {k: keyword_obj[k] for k in desired_order_list}
            keyword_dict.append(reordered_keyword_obj)

keyword_dict_sorted = sorted(keyword_dict, key=lambda d: [d['keyword'], d['pos'], d['modifier']]) 

output_json_fp = "test_keywords_list.json"
with open(output_json_fp, "wb+") as out_file:
    out_file.write(json.dumps(keyword_dict_sorted, option=json.OPT_INDENT_2))

excel_output_fp = "test_keywords_list.xlsx"
df1 = pd.DataFrame.from_dict(keyword_dict_sorted, orient="columns")
writer = pd.ExcelWriter(excel_output_fp, engine='xlsxwriter')
df1.to_excel(writer, sheet_name='shortlisted keywords')
workbook  = writer.book
worksheet = writer.sheets['shortlisted keywords']
worksheet.set_column(1, 14, 15)
writer.save()