"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
from game.console import ConsoleContainer, ConsoleHandler

from tcod.console import Console
from game.animation import AnimationHandler
import lzma
import pickle
import random
import string
import traceback
from typing import Optional
from utilities.set_interval import set_interval

import numpy as np
import tcod

import game.color as color
import game.entity_factories as entity_factories
import game.game_config as cfg
import game.input_handlers as input_handlers
from game.camera import Camera
from game.engine import Engine
from game.game_map import GameWorld
from game.tile_types import graphic_dt

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("data/menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = cfg.MAP_WIDTH
    map_height = cfg.MAP_HEIGHT

    room_max_size = 20
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)
    camera = Camera(width=cfg.CAMERA_WIDTH, height=cfg.CAMERA_HEIGHT)
    engine = Engine(player=player, camera=camera)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        camera=camera,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to a hacking game!", color.welcome_text
    )

    dagger = copy.deepcopy(entity_factories.dagger)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)

    dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message=False)

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self, animation_handler: Optional[AnimationHandler]):
        super().__init__(animation_handler)
        self.animation_handler = animation_handler
        self.animation_handler.add_animation('rain',
                                             self.rain(animation_handler.console_handler.root_console.width,
                                                       animation_handler.console_handler.root_console.height))

    class rain():
        """Animate the menu."""

        def __init__(self, width, height):
            self.generator = self.make_generator()
            self.width = width
            self.height = height
            self.duration = None
            self.frame_ratio = None

        def make_generator(self):
            items = [i for i in string.ascii_letters[:] +
                     '`~!@#$%^&*()_-+={[}|\:;"<>.?/']
            row = self.width
            column = self.height
            grid = np.full((row, column), fill_value=np.array(
                (ord('-'), color.black, color.black), dtype=graphic_dt), order='F')
            while True:
                for i in range(row):
                    for j in range(column):
                        ri = random.randrange(len(items))
                        randcolor = random.randint(0, 2)
                        fg_color = color.dark_green
                        if randcolor == 1:
                            fg_color = color.light_green
                        elif randcolor == 2:
                            fg_color = color.green
                        grid[i][j] = np.array(
                            (ord(items[ri]), fg_color, color.black), dtype=graphic_dt)
                yield ((0, row), (0, column), grid)

    def print_animation(self):
        """Print the animation to the console."""

    def on_render(self, console_handler: ConsoleHandler) -> None:
        """Render the main menu on a background image."""
        new_console = Console(24, 7, order='F')

        new_console.print(
            1,
            1,
            "Untitled Hacking Game",
            fg=color.menu_title,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            new_console.print(
                1,
                3 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
            )

        console = ConsoleContainer(
            new_console, (120-22)//2, 72//2, 0, 0, 0, 0, 1, 'main')
        console_handler.append(console)

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            self.animation_handler.remove_animation('rain')
            return input_handlers.MainGameEventHandler(new_game())

        return None
