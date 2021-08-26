from enum import auto, Enum


class RenderOrder(Enum):
    TERMINALS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
