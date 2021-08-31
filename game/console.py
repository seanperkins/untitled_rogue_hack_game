from typing import Optional
import tcod
from enum import auto, Enum


class ConsoleContainer:
    """
    Our version of a console
    """

    def __init__(self, console: tcod.Console, dest_x: int, dest_y: int, src_x: int, src_y: int,
                 width: int, height: int, z_index: int,
                 screen: str) -> None:
        """
        console (Console): The console.
        dest_x (int): Leftmost coordinate of the destination console.
        dest_y (int): Topmost coordinate of the destination console.
        src_x (int): X coordinate from this console to blit, from the left.
        src_y (int): Y coordinate from this console to blit, from the top.
        width (int): The width of the region to blit.

            If this is 0 the maximum possible width will be used.
        height (int): The height of the region to blit.

            If this is 0 the maximum possible height will be used.
        fg_alpha (float): Foreground color alpha vaule.
        bg_alpha (float): Background color alpha vaule.
        key_color (Optional[Tuple[int, int, int]]):
            None, or a (red, green, blue) tuple with values of 0-255.
        z_index (int): The z-index of the console.
        screen (Screen): The screen this console is on.
        """
        self.console = console
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.src_x = src_x
        self.src_y = src_y
        self.width = width
        self.height = height
        self.z_index = z_index
        self.screen = screen


class ConsoleHandler():
    """
    A class to combine all of our consoles in the correct order
    """

    def __init__(self, root_console: tcod.Console):
        self.consoles: list[ConsoleContainer] = []
        self.visible_screens = ['animation', 'main']
        self.root_console = root_console

    def display_screen(self, screen: str):
        """
        Display the given screen.
        """
        self.visible_screens.append(screen)

    def hide_screen(self, screen: str):
        """
        Hide the given screen.
        """
        self.visible_screens.remove(screen)

    def append(self, console: ConsoleContainer):
        self.consoles.append(console)

    def render(self):
        """
        Render all of our consoles
        """
        visible_consoles = [
            console for console in self.consoles if console.screen in self.visible_screens]
        sorted_consoles = sorted(
            visible_consoles, key=lambda x: x.z_index, reverse=False)
        for c in sorted_consoles:
            c.console.blit(self.root_console, c.dest_x, c.dest_y,
                           c.width, c.height, c.src_x, c.src_y)
        # Clear them so we can start again
        self.consoles = []
