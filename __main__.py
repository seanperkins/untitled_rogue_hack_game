#!/usr/bin/env python3
from tcod import console
from game.console import ConsoleHandler
from game.animation import AnimationHandler
import traceback

import tcod

import game.color as color
import game.exceptions as exceptions
import game.setup_game as setup_game
import game.input_handlers as input_handlers

import game.game_config as cfg


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    screen_height = cfg.SCREEN_HEIGHT
    screen_width = cfg.SCREEN_WIDTH

    tileset = tcod.tileset.load_tilesheet(*cfg.TILESET)

    # Start new game, don't waste time with menu.
    # handler: input_handlers.BaseEventHandler = input_handlers.MainGameEventHandler(
    #     setup_game.new_game())

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title=cfg.TITLE,
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        console_handler = ConsoleHandler(root_console)
        animation_handler = AnimationHandler(console_handler)
        handler: input_handlers.BaseEventHandler = setup_game.MainMenu(
            animation_handler=animation_handler)
        try:
            while True:
                root_console.clear()
                # The rendering order is wrong. I will need to create a renderering class
                # that can handle z-indexing so consoles can be sorted then drawn.
                animation_handler.draw_frame()
                handler.on_render(console_handler)
                console_handler.render()
                context.present(root_console)

                try:
                    for event in tcod.event.get():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


if __name__ == "__main__":
    main()
