from __future__ import annotations
from game.camera import Camera
from game.game_config import ACTIONS_HEIGHT, ACTIONS_WIDTH, CAMERA_HEIGHT, \
    CAMERA_WIDTH, LOG_HEIGHT, LOG_WIDTH, MAP_HEIGHT, MAP_WIDTH, \
    SIDEBAR_COMPONENT_HEIGHT, SIDEBAR_WIDTH

import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import game.exceptions as exceptions
from game.message_log import MessageLog
import game.render_functions as render_functions

if TYPE_CHECKING:
    from game.entity import Actor
    from game.game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld
    camera: Camera

    def __init__(self, player: Actor, camera: Camera,):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.camera = camera

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console) -> None:
        # Render frame with map inside
        render_functions.render_frame(
            console, 'GUI', 0, 0, CAMERA_WIDTH, CAMERA_HEIGHT)
        self.game_map.render(console)
        # Render sidebar
        render_functions.render_widget(
            console=console,
            widget='DIAGNOSTIC',
            x=CAMERA_WIDTH,
            y=0,
            width=SIDEBAR_WIDTH,
            height=SIDEBAR_COMPONENT_HEIGHT,
            render_function=render_functions.render_bar,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_widget(
            console=console,
            widget='CONTEXT',
            x=CAMERA_WIDTH,
            y=SIDEBAR_COMPONENT_HEIGHT,
            width=SIDEBAR_WIDTH,
            height=SIDEBAR_COMPONENT_HEIGHT,
            render_function=render_functions.render_names_at_mouse_location,
            engine=self,
        )

        render_functions.render_widget(
            console=console,
            widget='SPAWNED DAEMONS',
            x=CAMERA_WIDTH,
            y=SIDEBAR_COMPONENT_HEIGHT * 2,
            width=SIDEBAR_WIDTH,
            height=SIDEBAR_COMPONENT_HEIGHT,
            render_function=None,
        )

        render_functions.render_widget(
            console=console,
            widget='OBJECTIVES',
            x=CAMERA_WIDTH,
            y=SIDEBAR_COMPONENT_HEIGHT * 3,
            width=SIDEBAR_WIDTH,
            height=SIDEBAR_COMPONENT_HEIGHT,
            render_function=None,
        )

        render_functions.render_widget(
            console=console,
            widget='ACTION STACK',
            x=0,
            y=CAMERA_HEIGHT,
            width=ACTIONS_WIDTH,
            height=ACTIONS_HEIGHT,
            render_function=None,
        )

        render_functions.render_widget(
            console=console,
            widget='LOG',
            x=0,
            y=CAMERA_HEIGHT+ACTIONS_HEIGHT,
            width=LOG_WIDTH,
            height=LOG_HEIGHT,
            render_function=self.message_log.render,
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
