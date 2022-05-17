from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, Tuple
from typing import List

@dataclass_json
@dataclass
class Keyword:
    """
    A simple helper class for keywords adding a comparator for better readability
    """

    origin: List[str] = None
    source_word: str = None
    spacy_lemma: str = None
    nltk_lemma: str = None
    hard_lemma: Dict[str, str] = None
    keyword: str = None
    keyword_len: int = 0
    spacy_pos: str = None
    wordsAPI_pos: str = None
    pos: str = None
    spacy_occurrence: int = 0
    contained_words: List[str] = None
    phonetic_grade: str = None
    yake_rank: Tuple = None
    restrictions_before: List[str] = None
    restrictions_after: List[str] = None
    restrictions_as_joint: List[str] = None
    shortlist: str = None

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
