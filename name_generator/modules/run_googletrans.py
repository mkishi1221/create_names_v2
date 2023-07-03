from googletrans import Translator, LANGUAGES
import re

def get_translation(kw_list: list, input_lang: str, output_lang: str):
    translator = Translator()
    translations = translator.translate(kw_list, dest=output_lang, src=input_lang)
    translations_dict = {}
    for translation in translations:
        translated_text = re.sub(r"^\W+", "", translation.text).lower()
        translated_text = re.sub(r"\W+$", "", translated_text)
        if translation.origin != translated_text:
            translations_dict[translation.origin] = {output_lang: translated_text}
        else:
            translations_dict[translation.origin] = {output_lang: None}
    return translations_dict

def get_single_translation(text: str, input_lang: str, output_lang: str):
    translator = Translator()
    translation = translator.translate(text, dest=output_lang, src=input_lang)
    translated_text = re.sub(r"^\W+", "", translation.text).lower()
    translated_text = re.sub(r"\W+$", "", translated_text)
    if translation.origin == translated_text:
        translated_text = None
    language = LANGUAGES[output_lang]
    return translated_text, language