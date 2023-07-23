from ...modules.keyword_modifier import keyword_modifier
from ...classes.keyword_class import Keyword

keyword = Keyword.from_dict({'origin': ['keyword_list'], 'source_words': ['Vibrant'], 'spacy_lemma': None, 'nltk_lemma': 'vibrant', 'hard_lemma': None, 'spacy_pos': None, 'eng_dict_pos': ['adjective'], 'keyword_len': 7, 'spacy_occurrence': 0, 'contained_words': ['ant', 'bra', 'bran', 'brant', 'rant'], 'phonetic_score': 0.04394110742358322, 'lowest_phonetic': 0.002046710622867963, 'implausible_chars': [], 'components': ['vi·brant'], 'abbreviations': ['vi', 'vib', 'vibra'], 'restrictions_before': None, 'restrictions_after': None, 'restrictions_as_joint': None, 'yake_score': 0.0339251285730776, 'yake_rank': 59.0, 'keyword_class': 'prime', 'keyword': 'vibrant', 'pos': 'adjective', 'shortlist': 's'})

def test_keyword_modifier_ab_cut():
    # arrange
    # act
    res = keyword_modifier(keyword, "ab_cut", {})
    # assert
    assert res is not None
    assert res[0].modifier == "ab_cut"
    assert res[0].modword == "vi"

def test_keyword_modifier_ms_cut():
    # arrange
    # act
    res = keyword_modifier(keyword, "ms_cut", {})
    # assert
    assert res is not None
    assert res[0].modword == "vibrantt"
    assert res[1].modword == "vibranta"