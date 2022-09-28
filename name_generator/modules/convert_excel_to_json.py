#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
import pandas as pd
import orjson as json

def convert_to_list(string: str):
    if len(str(string or "")) > 0:
        try:
            str_list = string.replace('[', '').replace(']', '').replace('\"', '').replace(' ', '').replace('\'', '').split(",")
            # str_list = list(filter(None, str_list))
        except AttributeError:
            raise Exception(f"Attribute error: {string}")
    else:
        str_list = None
    return str_list

def convert_excel_to_json(input_excel_fp, target_sheet: str = None, target_sheets: List[str] = None, output_json_fp: str = None, convert_list: str = None):

    if target_sheet is None and target_sheets is None:
        sheet_list = ["Sheet1"]
    
    elif target_sheet is not None and target_sheets is None:
        sheet_list = [target_sheet]

    elif target_sheet is None and target_sheets is not None:
        sheet_list = target_sheets

    else:
        sheet_list = target_sheets.append(target_sheet)

    list_of_dict = []

    for sheet in sheet_list:

        # Convert excel data into pandas dataframe
        excel_data_df = pd.read_excel(input_excel_fp, sheet_name=sheet, index_col=0)

        # Convert NaN into ""
        excel_data_df = excel_data_df.fillna('')

        # Convert df to list of dicts and convert to json format
        if convert_list is not None:
            excel_data_list = excel_data_df.to_dict(orient='records')
            new_excel_data_list = []
            for dict_obj in excel_data_list:
                new_dict_obj = {}
                for key, item in dict_obj.items():
                    if type(item) == str and item.startswith("[") and item.endswith("]"):
                        new_item = convert_to_list(item)
                        new_dict_obj[key] = new_item
                    else:
                        new_dict_obj[key] = item
                list_of_dict.append(new_dict_obj)
        else:
            list_of_dict.extend(excel_data_df.to_dict(orient='records'))

    # Create output file path (save as .json file as same name in same location)
    if output_json_fp is None:
        output_json_fp = "".join([input_excel_fp[:-5], ".json"])
    
    # Save json file
    with open(output_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(list_of_dict, option=json.OPT_INDENT_2))

    # Return output filepath
    return output_json_fp