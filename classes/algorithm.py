from typing import List
from pydantic.dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Algorithm:
    """
    Helper class for manipulation of keywords
    """

    id: int
    components: List[tuple]

    def __init__(self, id: int, components: List[tuple]):
        self.components = components
        self.id = hash("".join([i for sub in components for i in sub]))

    def __eq__(self, o: object) -> bool:
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return self.id != o.id

    def __hash__(self) -> int:
        return hash("".join([i for sub in self.components for i in sub]))

    def __repr__(self) -> str:
        return " + ".join(map(lambda x: str(x[0]) + '(' + str(x[1]) + ')', self.components))

    def __len__(self) -> int:
        return len(self.components)

