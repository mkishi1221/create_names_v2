#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from classes.name_class import Etymology
from typing import List, Dict

@dataclass_json
@dataclass
class Domain:
    domain: str = None
    availability: str = None
    last_checked: str = None
    data_valid_till: str = None
    shortlist: str = None

    def __eq__(self, o: object) -> bool:
        return self.domain == o.domain

    def __ne__(self, o: object) -> bool:
        return self.domain != o.domain

    def __hash__(self) -> int:
        return hash((self.domain, self.availability, self.last_checked, self.data_valid_till, self.shortlist))

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
class NameDomain:
    name_in_lower: str = None
    length: int = 0
    length_score: int = 0
    total_score: int = 0
    avail_domains: List[Domain] = field(default_factory=list)
    not_avail_domains: List[Domain] = field(default_factory=list)
    etymologies: Dict[str, Etymology] = None

    def __eq__(self, o: object) -> bool:
        return self.name_in_lower == o.name_in_lower
    
    def __ne__(self, o: object) -> bool:
        return self.name_in_lower != o.name_in_lower

    def __hash__(self) -> int:
        return hash((self.name_in_lower, self.length, self.length_score, self.total_score, self.avail_domains, self.not_avail_domains, self.etymologies))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )