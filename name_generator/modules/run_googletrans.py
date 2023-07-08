from googletrans import Translator, LANGUAGES
from ai4bharat.transliteration import XlitEngine
from unidecode import unidecode
import re
import os, sys

alphabet = "abcdefghijklmnopqrstuvwxyz"

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def get_translation(kw_list: list, input_lang: str, output_lang: str):
    translator = Translator()
    translations = translator.translate(kw_list, dest=output_lang, src=input_lang)
    translations_dict = {}
    for translation in translations:
        if output_lang == "mr":
            translated_text = translation.text
            with HiddenPrints():
                e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)
                translated_text = e.translit_word(translated_text, lang_code=output_lang, topk=1)[0]
        else:
            translated_text = unidecode(translation.text)
        translated_text = re.sub(r"^\W+", "", translated_text).lower()
        translated_text = re.sub(r"\W+$", "", translated_text)
        if translation.origin != translated_text or all(letter in alphabet for letter in translated_text):
            translations_dict[translation.origin] = {output_lang: translated_text}
        else:
            translations_dict[translation.origin] = {output_lang: None}
    return translations_dict

def get_single_translation(text: str, input_lang: str, output_lang: str):
    translator = Translator()
    translation = translator.translate(text, dest=output_lang, src=input_lang)
    if output_lang == "mr":
        translated_text = translation.text
        with HiddenPrints():
            e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)
            translated_text = e.translit_word(translated_text, lang_code=output_lang, topk=1)[0]
    else:
        translated_text = unidecode(translation.text)
    translated_text = re.sub(r"^\W+", "", translated_text).lower()
    translated_text = re.sub(r"\W+$", "", translated_text)
    if translation.origin == translated_text or not all(letter in alphabet for letter in translated_text):
        translated_text = None
    language = LANGUAGES[output_lang]
    return translated_text, language