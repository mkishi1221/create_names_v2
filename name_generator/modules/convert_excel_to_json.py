#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import List
import pandas as pd
import orjson as json

def convert_to_list(string: str):
    if type(string) == str:
        if len(str(string or "")) > 0:
            try:
                str_list = string.replace('[', '').replace(']', '').replace('\"', '').replace(' ', '').replace('\'', '').split(",")
                str_list = list(filter(None, str_list))
                if len(str_list) == None:
                    str_list = None
            except AttributeError:
                raise Exception(f"Attribute error: {string}")
        else:
            str_list = None
    else:
        str_list = string
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
            for dict_obj in excel_data_list:
                new_dict_obj = {}
                for key, item in dict_obj.items():

                    if type(item) == str and item.startswith("[") and item.endswith("]"):
                        item = convert_to_list(item)
                        new_dict_obj[key] = item
                    if type(item) == str and len(item) == 0:
                        new_dict_obj[key] = None
                    else:
                        new_dict_obj[key] = item

                    #testing_start
                    # item_type = type(item)
                    # if item_type is str:
                    #     item_starts_with = item.startswith("[")
                    #     item_ends_with = item.endswith("]")
                    #     item_starts_with_str = f"starts with [: {item_starts_with}"
                    #     item_ends_with_str = f"ends with ]: {item_ends_with}"
                    #     print(item_type, "|", item, "|", item_starts_with_str, "|", item_ends_with_str, "|", item)
                    #testing_end

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