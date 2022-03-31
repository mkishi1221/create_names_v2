from dataclasses import dataclass, field
from classes.name_style_class import Name_Style
from typing import List, Dict

@dataclass
class Etymology:
    name_in_title: str = None
    keywords: List[str] = field(default_factory=list)
    name_styles: List[Name_Style] = field(default_factory=list)

    def __eq__(self, o: object) -> bool:
        return self.name_in_title == o.name_in_title

    def __ne__(self, o: object) -> bool:
        return self.name_in_title != o.name_in_title

    def __hash__(self) -> int:
        return hash(
            (
                self.name_in_title,
                self.keywords,
                self.name_styles,
            )
        )

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )




@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    keywords list will contain tuples that contain (keyword, pos, modifier)
    """

    name_in_lower: str = None
    length: int = 0
    length_score: int = 0
    total_score: int = 0
    phonetic_pattern: str = None
    phonetic_count: dict = None
    word_plausibility: str = None
    is_word: str = None
    shortlist: str = None
    etymologies: Dict[str, Etymology] = None

    def __eq__(self, o: object) -> bool:
        return self.name_in_lower == o.name_in_lower

    def __ne__(self, o: object) -> bool:
        return self.name_in_lower != o.name_in_lower

    def __hash__(self) -> int:
        return hash(
            (
                self.length,
                self.name_in_lower,
                self.length_score,
                self.total_score,
            )
        )

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )

@dataclass
class Domain:
    domain: str = None
    availability: str = None
    last_checked: str = None
    check_validity: str = None

@dataclass
class NameDomain:
    domain: List[Domain] = field(default_factory=list)