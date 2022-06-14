#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from classes.name_class import Etymology
from classes.name_class import Graded_name
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
    name_in_title: Graded_name.name_in_lower = None
    name_in_lower: Graded_name.name_in_title = None
    name_type: Graded_name.name_type = None
    length: Graded_name.length = 0
    phonetic_grade: Graded_name.phonetic_grade = None
    keywords: Graded_name.keywords = None
    keyword_combinations: Graded_name.keyword_combinations = None
    pos_combinations: Graded_name.pos_combinations = None
    modifier_combinations: Graded_name.modifier_combinations = None
    etymologies: Graded_name.etymologies = None
    avail_domains: List[Domain] = None
    not_avail_domains: List[Domain] = None
    grade: Graded_name.grade = None

    def __eq__(self, o: object) -> bool:
        return self.name_in_lower == o.name_in_lower
    
    def __ne__(self, o: object) -> bool:
        return self.name_in_lower != o.name_in_lower

    def __hash__(self) -> int:
        return hash((self.name_in_lower, self.length, self.avail_domains, self.not_avail_domains, self.etymologies))

    def __repr__(self) -> str:
        return str(
            {
                key: self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        )