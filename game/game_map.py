from __future__ import annotations
from game.camera import Camera
from game.render_functions import render_frame

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from game.entity import Actor, Item
import game.tile_types as tile_types
import game.color as color

if TYPE_CHECKING:
    from game.engine import Engine
    from game.entity import Entity


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, camera: Camera, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.camera = camera
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full(
            (self.width, self.height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (self.width, self.height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (self.width, self.height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        (x, y) = self.camera.x, self.camera.y

        (height, width) = self.camera.height, self.camera.width

        tiles_in_frame = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )
        rows_to_delete = [n for n in range(
            0, x)] + [n for n in range(x + width, len(tiles_in_frame))]
        columns_to_delete = [n for n in range(
            0, y)] + [n for n in range(y + height, len(tiles_in_frame[0]))]

        tiles_in_frame = np.delete(tiles_in_frame, rows_to_delete, axis=0)
        tiles_in_frame = np.delete(tiles_in_frame, columns_to_delete, axis=1)

        new_console = Console(width, height, 'F')
        # Remember that tiles is the raw 2d tiles array
        new_console.tiles_rgb[0: width, 0: height] = tiles_in_frame

        entities_in_frame = [entity for entity in self.entities if entity.x >=
                             x and entity.y >= y and entity.x < x + self.camera.map_width and entity.y < y + self.camera.map_height]

        entities_sorted_for_rendering = sorted(
            entities_in_frame, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            if self.visible[entity.x, entity.y]:
                new_console.print(
                    x=entity.x - x, y=entity.y - y, string=entity.char, fg=entity.color
                )
        new_console.blit(console, 1, 1, 0, 0, width, height)


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        camera: Camera,
        current_floor: int = 0,
    ):
        self.engine = engine
        self.camera = camera

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from game.procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
            camera=self.camera,
        )
