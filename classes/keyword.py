from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, Optional


@dataclass_json
@dataclass
class Keyword:
    """
    A simple helper class for keywords adding a comparator for better readability
    """

    origin: list[str] = None
    source_word: str = None
    spacy_lemma: str = None
    keyword: str = None
    keyword_len: int = 0
    spacy_pos: str = None
    wordsAPI_pos: str = None
    pos: str = None
    spacy_occurrence: int = 0
    pairing_limitations: str = "none"

    def __eq__(self, o: object) -> bool:
        return self.source_word == o.source_word and self.keyword == o.keyword and self.pos == o.pos

    def __ne__(self, o: object) -> bool:
        return self.source_word != o.source_word and self.keyword != o.keyword and self.pos != o.pos

    def __hash__(self) -> int:
        return hash((self.source_word, self.keyword_len, self.keyword, str(self.origin)))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )

@dataclass_json
@dataclass
class Modword(Keyword):
    modifier: str = "no_mod"
    modword: str = ""
    modword_len: int = 0

    def __init__(
        self,
        origin,
        source_word,
        spacy_lemma,
        keyword,
        keyword_len,
        spacy_pos,
        wordsAPI_pos,
        pos,
        spacy_occurrence,
        pairing_limitations,
        modifier,
        modword,
        modword_len
    ):
        self.origin = origin
        self.source_word = source_word
        self.spacy_lemma = spacy_lemma
        self.keyword = keyword
        self.keyword_len = keyword_len
        self.spacy_pos = spacy_pos
        self.wordsAPI_pos = wordsAPI_pos
        self.pos = pos
        self.spacy_occurrence = spacy_occurrence
        self.pairing_limitations = pairing_limitations
        self.modifier = modifier
        self.modword = modword
        self.modword_len = modword_len

    def __eq__(self, o: object) -> bool:
        return self.modword == o.modword and self.keyword == o.keyword and self.wordsAPI_pos == o.wordsAPI_pos

    def __ne__(self, o: object) -> bool:
        return self.modword != o.modword and self.keyword != o.keyword and self.wordsAPI_pos != o.wordsAPI_pos

    def __hash__(self) -> int:
        return hash((self.source_word, self.keyword_len, self.keyword, self.modword, self.origin))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )
