import pandas as pd
import orjson as json


def convert_excel_to_json(input_excel_fp, target_sheet_name):

    # Convert excel data into pandas dataframe
    excel_data_df = pd.read_excel(input_excel_fp, sheet_name=target_sheet_name, index_col=0)

    # Convert NaN into ""
    excel_data_df = excel_data_df.fillna('')
    
    # Create output file path (save as .json file as same name in same location)
    output_json_fp = "".join([input_excel_fp[:-5], ".json"])

    # Export dataframe to json format
    json_str = excel_data_df.to_json(orient='records')

    # Save json file
    with open(output_json_fp, "wb+") as out_file:
        out_file.write(json.dumps(json.loads(json_str), option=json.OPT_INDENT_2))

    # Return output filepath
    return output_json_fp