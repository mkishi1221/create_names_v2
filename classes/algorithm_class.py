from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Tuple

@dataclass_json
@dataclass
class Component:

    pos: str = None
    modifier: str = None

    def __init__(self, pos: str, modifier: str):
        self.pos = pos
        self.modifier = modifier

    def __eq__(self, o: object) -> bool:
        return self.pos == o.pos and self.modifier == o.modifier

    def __ne__(self, o: object) -> bool:
        return self.pos != o.pos and self.modifier != o.modifier

    def __hash__(self) -> int:
        return hash((self.pos, self.modifier))

    def __repr__(self) -> str:
        return "".join([str(self.pos), " (", str(self.modifier), ")"])

@dataclass_json
@dataclass
class Algorithm:
    
    """
    Helper class for manipulation of keywords
    Components are stored in a list of component/modifier pairs
    """

    id: int = 0
    components: Tuple[Component] = None

    def __init__(self, id: int, components: str):
        self.id = hash("".join(str(x) for x in components))
        self.components = components
        
    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return self.id != o.id

    def __hash__(self) -> int:
        return hash("".join(str(x) for x in self.components))

    def __repr__(self) -> str:
        return " + ".join(map(lambda x: str(x.pos) + '(' + str(x.modifier) + ')', self.components))

    def __len__(self) -> int:
        return len(self.components)

