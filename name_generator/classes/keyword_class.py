from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict
from typing import List

@dataclass_json
@dataclass
class Keyword:
    """
    A simple helper class for keywords adding a comparator for better readability
    """

    origin: List[str] = None
    source_words: List[str] = None
    spacy_lemma: str = None
    nltk_lemma: str = None
    hard_lemma: Dict[str, str] = None
    spacy_pos: str = None
    eng_dict_pos: List[str] = None
    keyword_len: int = 0
    spacy_occurrence: int = 0
    contained_words: List[str] = None
    phonetic_score: int = None
    lowest_phonetic: str = None
    implausible_chars: List[str] = None
    components: str = None
    abbreviations: List[str] = None
    restrictions_before: List[str] = None
    restrictions_after: List[str] = None
    restrictions_as_joint: List[str] = None
    yake_score: int = None
    yake_rank: int = None
    keyword_class: str = None
    keyword: str = None
    pos: str = None
    shortlist: str = None

    def __eq__(self, o: object) -> bool:
        return self.keyword == o.keyword and self.pos == o.pos

    def __ne__(self, o: object) -> bool:
        return self.keyword != o.keyword and self.pos != o.pos

    def __hash__(self) -> int:
        return hash((self.keyword_len, self.keyword, self.pos, str(self.origin)))

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
    modifier: str = "no_cut"
    modword: str = ""
    modword_len: int = 0
    lang: str = "english"
    translation: str = None

    def __eq__(self, o: object) -> bool:
        return self.modword == o.modword and self.keyword == o.keyword and self.pos == o.pos

    def __ne__(self, o: object) -> bool:
        return self.modword != o.modword and self.keyword != o.keyword and self.pos != o.pos

    def __hash__(self) -> int:
        return hash((self.keyword_len, self.keyword, self.modword, self.pos))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )