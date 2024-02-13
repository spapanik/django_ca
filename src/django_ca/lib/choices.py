from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from secrets import choice
from typing import Any, Self


@dataclass(frozen=True)
class ChoiceValue:
    key: str
    label: str
    obj: Any


class Choices(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, _start: int, _count: int, _last_values: list[ChoiceValue]
    ) -> ChoiceValue:
        label = name.replace("_", " ").title()
        return ChoiceValue(name, label, name)

    def __init__(self, value: ChoiceValue) -> None:
        self.key = value.key
        self.label = value.label
        self.obj = value.obj

    @classmethod
    def random(cls) -> Self:
        return choice(list(cls))

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.key, item.label) for item in cls]

    @classmethod
    def names(cls) -> Iterator[str]:
        for item in cls:
            yield item.name

    @classmethod
    def values(cls) -> Iterator[ChoiceValue]:
        for item in cls:
            yield item.value

    @classmethod
    def keys(cls) -> Iterator[str]:
        for item in cls:
            yield item.key

    @classmethod
    def labels(cls) -> Iterator[str]:
        for item in cls:
            yield item.label

    @classmethod
    def objects(cls) -> Iterator[Any]:
        for item in cls:
            yield item.obj
