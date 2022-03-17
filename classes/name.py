from dataclasses import dataclass, field
from classes.algorithm import Algorithm

@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    keywords list will contain tuples that contain (keyword, pos, modifier)
    """

    name: str = ""
    length: int = 0
    keyword_score: int = 0
    length_score: int = 0
    score: int = 0
    algorithm: Algorithm = ""
    keywords: list[tuple] = field(default_factory=list)

    def __eq__(self, o: object) -> bool:
        return self.name == o.name

    def __ne__(self, o: object) -> bool:
        return self.name != o.name

    def __hash__(self) -> int:
        return hash(
            (
                self.length,
                self.name,
                self.name_length_score,
                self.name_score,
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

class Domain(Name):

    # domain list will contain tuples showing (domain, availability)

    tld_list: list[str] = field(default_factory=list)
    domain: list[tuple] = field(default_factory=list)
