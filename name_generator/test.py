#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from modules.convert_excel_to_json import convert_excel_to_json

project_id = "masayuki"
project_path = f"projects/{project_id}"
keyword_fp = f"{project_path}/results/{project_id}_keywords.xlsx"
keywords_json_fp: str = f"{project_path}/tmp/logs/{project_id}_keywords.json"
sheets = ["nouns", "verbs", "adjectives", "adverbs"]

keywords_json_mfp = convert_excel_to_json(keyword_fp, target_sheets=sheets, output_json_fp=keywords_json_fp, convert_list=True)

