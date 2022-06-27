#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dataclasses import dataclass
from classes.algorithm_class import Component
from classes.keyword_class import Modword
from typing import List, Dict, Tuple

@dataclass
class Etymology:
    name_in_title: str = None
    modword_tuple: Tuple[str] = None
    keyword_tuple: Tuple[Modword.keyword] = None
    pos_tuple: Tuple[Component.pos] = None
    modifier_tuple: Tuple[Component.modifier] = None
    exempt_contained: List[str] = None
    name_type: str = None

    def __eq__(self, o: object) -> bool:
        return (
            self.name_in_title == o.name_in_title
            and self.modword_tuple == o.modword_tuple
            and self.keyword_tuple == o.keyword_tuple
            and self.modifier_tuple == o.modifier_tuple
            and self.pos_tuple == o.pos_tuple
        )

    def __ne__(self, o: object) -> bool:
        return (
            self.name_in_title != o.name_in_title
            and self.modword_tuple != o.modword_tuple
            and self.keyword_tuple != o.keyword_tuple
            and self.modifier_tuple != o.modifier_tuple
            and self.pos_tuple != o.pos_tuple
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.name_in_title,
                self.modword_tuple,
                self.keyword_tuple,
                self.modifier_tuple,
                self.pos_tuple,
                self.name_type
            )
        )

    def __repr__(self) -> str:

        algorithm_list = []
        for index in range(len(self.pos_tuple)):
            algorithm_list.append(f"{self.modword_tuple[index]}({self.keyword_tuple[index]}|{self.pos_tuple[index]})")
        return "+".join(algorithm_list)

@dataclass
class Name:
    """
    A simple helper class for Names adding a comparator for better readability
    keywords list will contain tuples that contain (keyword, pos, modifier)
    """

    name_in_lower: str = None
    length: int = 0
    phonetic_pattern: str = None
    phonetic_grade: str = None
    implaus_chars: int = None
    is_word: str = None
    exempt_contained: List[str] = None
    contained_words: List[str] = None
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
class Graded_name:

    name_in_lower: Name.name_in_lower = None
    name_in_title: Etymology.name_in_title = None
    name_type: Etymology.name_type = None
    length: Name.length = 0
    phonetic_pattern: Name.phonetic_pattern = None
    phonetic_grade: Name.phonetic_grade = None
    implaus_chars: Name.implaus_chars = None
    is_word: Name.is_word = None
    exempt_contained: Name.exempt_contained = None
    contained_words: List[str] = None
    wiki_title: str = None
    modwords: List[str] = None
    keywords: List[str] = None
    keyword_combinations: List[str] = None
    pos_combinations: List[str] = None
    modifier_combinations: List[str] = None
    etymologies: List[Etymology] = None
    grade: str = None

    def __eq__(self, o: object) -> bool:
        return self.name_in_title == o.name_in_title and self.name_type == o.name_type

    def __ne__(self, o: object) -> bool:
        return self.name_in_title != o.name_in_title and self.name_type != o.name_type

    def __hash__(self) -> int:
        return hash(
            (
                self.length,
                self.name_in_lower,
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