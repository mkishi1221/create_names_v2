from dataclasses import dataclass, field
from classes.algorithm import Algorithm
from classes.algorithm import Component
from typing import List

@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    keywords list will contain tuples that contain (keyword, pos, modifier)
    """

    name_lower: str = None
    name_title: List[str] = field(default_factory=list)
    length: int = 0
    length_score: int = 0
    total_score: int = 0
    keywords: List[str] = field(default_factory=list)
    algorithm: List[Algorithm] = field(default_factory=list)

    def __eq__(self, o: object) -> bool:
        return self.name_lower == o.name_lower

    def __ne__(self, o: object) -> bool:
        return self.name_lower != o.name_lower

    def __hash__(self) -> int:
        return hash(
            (
                self.length,
                self.name_lower,
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
class Domain(Name):

    # domain list will contain tuples showing (domain, availability)

    tld_list: List[str] = field(default_factory=list)
    domain: List[tuple] = field(default_factory=list)
