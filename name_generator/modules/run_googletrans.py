from googletrans import Translator
import orjson as json
import re

def get_translation(kw_list: list, output_fp):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translator = Translator()
    # translate into Latin
    translations = translator.translate(kw_list, dest='la')
    translations_dict = {}
    for translation in translations:
        translated_text = re.sub(r"^\W+", "", translation.text).lower()
        translated_text = re.sub(r"\W+$", "", translated_text)
        if translation.origin != translated_text:
            translations_dict[translation.origin] = {"latin": translated_text}
        else:
            translations_dict[translation.origin] = {"latin": None}


    with open(output_fp, "wb+") as out_file:
        out_file.write(json.dumps(translations_dict, option=json.OPT_INDENT_2))