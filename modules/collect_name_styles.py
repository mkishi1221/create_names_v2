from classes.name_style_class import Name_Style
from classes.name_style_class import Component
import orjson as json
from typing import List

# Input is a file path
def collect_name_styles(name_styles_fp: str) -> List[Name_Style]:

    # Import Name Style list from xlsx file
    with open(name_styles_fp) as name_styles_file:
        name_style_data = json.loads(name_styles_file.read())

    name_styles = set()

    for name_style in name_style_data:
        comp_list = []
        if name_style["deactivate"] == "":
            if name_style["keyword_type_1"] != "":
                comp_list.append(Component(keyword_type=name_style["keyword_type_1"], modifier=name_style["modifier_1"]))
            if name_style["keyword_type_2"] != "":
                comp_list.append(Component(keyword_type=name_style["keyword_type_2"], modifier=name_style["modifier_2"]))
            if name_style["keyword_type_3"] != "":
                comp_list.append(Component(keyword_type=name_style["keyword_type_3"], modifier=name_style["modifier_3"]))

            name_styles.add(Name_Style(0, comp_list))

    return list(name_styles)
