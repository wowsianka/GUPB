from __future__ import annotations
from abc import ABC, abstractmethod
from typing import NamedTuple, List

from gupb.model import arenas
from gupb.model import characters
from gupb.model import coordinates
from gupb.model import effects


class WeaponDescription(NamedTuple):
    name: str


class Weapon(ABC):
    def description(self) -> WeaponDescription:
        return WeaponDescription(self.__class__.__name__.lower())

    @classmethod
    @abstractmethod
    def cut_positions(
            cls,
            terrain: arenas.Terrain,
            position: coordinates.Coords,
            facing: characters.Facing
    ) -> List[coordinates.Coords]:
        raise NotImplementedError

    @abstractmethod
    def cut(self, arena: arenas.Arena, position: coordinates.Coords, facing: characters.Facing) -> None:
        raise NotImplementedError

    @staticmethod
    def cut_transparent(arena: arenas.Arena, position: coordinates.Coords) -> None:
        if position in arena.terrain and arena.terrain[position].terrain_transparent():
            arena.register_effect(effects.WeaponCut(), position)


class LineWeapon(Weapon, ABC):
    @staticmethod
    @abstractmethod
    def reach() -> int:
        raise NotImplementedError

    @classmethod
    def cut_positions(
            cls,
            terrain: arenas.Terrain,
            position: coordinates.Coords,
            facing: characters.Facing
    ) -> List[coordinates.Coords]:
        cut_positions = []
        cut_position = position
        for _ in range(cls.reach()):
            cut_position += facing.value
            if cut_position not in terrain:
                break
            cut_positions.append(cut_position)
            if not terrain[cut_position].transparent:
                break
        return cut_positions

    def cut(self, arena: arenas.Arena, position: coordinates.Coords, facing: characters.Facing) -> None:
        for cut_position in self.cut_positions(arena.terrain, position, facing):
            self.cut_transparent(arena, cut_position)


class Knife(LineWeapon):
    @staticmethod
    def reach() -> int:
        return 1


class Sword(LineWeapon):
    @staticmethod
    def reach() -> int:
        return 3


class Bow(LineWeapon):
    def __init__(self):
        self.ready: bool = False

    def description(self) -> WeaponDescription:
        return WeaponDescription(f"{self.__class__.__name__.lower()}_{'loaded' if self.ready else 'unloaded'}")

    @staticmethod
    def reach() -> int:
        return 50

    def cut(self, arena: arenas.Arena, position: coordinates.Coords, facing: characters.Facing) -> None:
        if self.ready:
            super().cut(arena, position, facing)
            self.ready = False
        else:
            self.ready = True


class Axe(Weapon):
    @classmethod
    def cut_positions(
            cls,
            terrain: arenas.Terrain,
            position: coordinates.Coords,
            facing: characters.Facing
    ) -> List[coordinates.Coords]:
        centre_position = position + facing.value
        left_position = centre_position + facing.turn_left().value
        right_position = centre_position + facing.turn_right().value
        return [left_position, centre_position, right_position]

    def cut(self, arena: arenas.Arena, position: coordinates.Coords, facing: characters.Facing) -> None:
        for cut_position in self.cut_positions(arena.terrain, position, facing):
            self.cut_transparent(arena, cut_position)


class Amulet(Weapon):

    @classmethod
    def cut_positions(
            cls,
            terrain: arenas.Terrain,
            position: coordinates.Coords,
            facing: characters.Facing
    ) -> List[coordinates.Coords]:
        return [
            coordinates.Coords(*position + (1, 1)),
            coordinates.Coords(*position + (-1, 1)),
            coordinates.Coords(*position + (1, -1)),
            coordinates.Coords(*position + (-1, -1)),
            coordinates.Coords(*position + (2, 2)),
            coordinates.Coords(*position + (-2, 2)),
            coordinates.Coords(*position + (2, -2)),
            coordinates.Coords(*position + (-2, -2)),
        ]

    def cut(self, arena: arenas.Arena, position: coordinates.Coords, facing: characters.Facing) -> None:
        for cut_position in self.cut_positions(arena.terrain, position, facing):
            self.cut_transparent(arena, cut_position)
