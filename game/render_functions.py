from __future__ import annotations

from typing import Tuple, TYPE_CHECKING, Any


import game.color as color

if TYPE_CHECKING:
    from tcod import Console
    from game.engine import Engine
    from game.game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(
        console: Console, x, y, width, height, current_value: int, maximum_value: int, total_width: int,
        *args, **kwargs) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=width, height=1,
                      ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=x, y=y, width=width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=x+1, y=y, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )


def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(
    console: Console, x: int, y: int, engine: Engine, *args, **kwargs,
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)


def render_frame(console: Console, label: str, x: int, y: int, width: int, height: int) -> None:
    console.draw_frame(x, y, width, height, fg=color.light_green)
    console.print(x=x + 1, y=y, string=label, fg=color.light_green)


def render_widget(
    console: Console,
    widget: str,
    x: int,
    y: int,
    width: int,
    height: int,
    render_function: Any,
    *args,
    **kwargs,
) -> None:
    render_frame(console, widget, x, y, width, height)
    if render_function is not None:
        render_function(console=console, x=x+1, y=y+1, width=width-2,
                        height=height-2, *args, **kwargs)
