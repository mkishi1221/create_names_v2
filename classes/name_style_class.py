from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List

@dataclass_json
@dataclass
class Component:

    keyword: str = None
    modword: str = None
    keyword_type: str = None
    modifier: str = None

    def __init__(self, keyword_type: str, modifier: str):
        self.keyword_type = keyword_type
        self.modifier = modifier

    def __eq__(self, o: object) -> bool:
        return self.keyword_type == o.keyword_type and self.modifier == o.modifier

    def __ne__(self, o: object) -> bool:
        return self.keyword_type != o.keyword_type and self.modifier != o.modifier

    def __hash__(self) -> int:
        return hash((self.keyword_type, self.modifier))

    def __repr__(self) -> str:
        return "".join([str(self.keyword), "|", str(self.keyword_type), " (", str(self.modifier), ")"])

@dataclass_json
@dataclass
class Name_Style:
    """
    Helper class for manipulation of keywords
    Components are stored in a list of component/modifier pairs
    """

    id: int = 0
    components: List[Component] = field(default_factory=list)

    def __init__(self, id: int, components: List[Component]):
        self.components = components
        self.id = hash("".join(str(x) for x in components))

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return self.id != o.id

    def __hash__(self) -> int:
        return hash("".join(str(x) for x in self.components))

    def __repr__(self) -> str:
        if self.components[0].keyword is None:
            name_style = " + ".join(map(lambda x: str(x.keyword_type) + '(' + str(x.modifier) + ')', self.components))
        else:
            name_style = " + ".join(map(lambda x: str(x.keyword) + "|" + str(x.keyword_type) + '(' + str(x.modifier) + ')', self.components))
        return name_style

    def __len__(self) -> int:
        return len(self.components)
