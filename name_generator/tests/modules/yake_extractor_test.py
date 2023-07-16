from ...modules.yake_keyword_extractor import keyword_extractor
import yake

class MockExtractor:

    @staticmethod
    def extract_keywords(text: str):
        return [("test", "0.15831692877998726")]

def mock_keword_extractor(*args, **kwargs):
    return MockExtractor()

def test_extract_returns_none_when_no_keywords_nor_sentences(tmp_path):
    # arrange
    # act
    res = keyword_extractor(f"{tmp_path}/test.json")
    # assert
    assert res is None

def test_extract_returns_keywords(tmp_path, monkeypatch):
    # arrange
    monkeypatch.setattr(yake, "KeywordExtractor", mock_keword_extractor)
    # act
    res = keyword_extractor(f"{tmp_path}/test.json", None, ["hi", "I", "am", "test"])
    # assert
    assert res == {'test': (1, '0.15831692877998726')}

def test_extract_returns_sentences(tmp_path, monkeypatch):
    # arrange
    monkeypatch.setattr(yake, "KeywordExtractor", mock_keword_extractor)
    # act
    res = keyword_extractor(f"{tmp_path}/test.json", "Hi I am test")
    # assert
    assert res == {"test": (1, '0.15831692877998726')}

def test_extract_returns_sentences_and_keywords(tmp_path, monkeypatch):
    # arrange
    monkeypatch.setattr(yake, "KeywordExtractor", mock_keword_extractor)
    # act
    res = keyword_extractor(f"{tmp_path}/test.json", "Hi I am test", ["hi", "I", "am", "test"])
    # assert
    assert res == {'test': (1, '0.15831692877998726')}

