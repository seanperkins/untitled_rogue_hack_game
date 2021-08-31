import tcod
import time

FPS = 60
SECONDS_PER_FRAME = 1 / FPS


class AnimationHandler:
    """
    AnimationHandler handles the animation of the game.
    """

    def __init__(self, console: tcod.Console):
        """
        Initialize the AnimationHandler.

        :param console: The root console to blit animation console to
        """
        self.console = console
        self.animations = {}

        self.oldTime = 0
        self.oldFrame = None

        self.frame_number = 1
        self.animation_frames = {}

    def add_animation(self, name, animation):
        """
        Add an animation to the handler.

        :param animation: The animation to add.
        """
        self.animations[name] = animation

    def remove_animation(self, name):
        """
        Remove an animation from the handler.

        :param name: The name of the animation to remove.
        """
        self.animations.pop(name)

    def draw_frame(self):
        """
        Draw the next frame of the animations.
        """
        if len(self.animations) == 0:
            return
        if self.frame_number > 60:
            self.frame_number = 1
        else:
            self.frame_number += 1

        currentTime = time.time()
        if (currentTime - self.oldTime) > SECONDS_PER_FRAME:
            animation_console = tcod.Console(
                self.console.width, self.console.height, order='F')
            for name, animation in self.animations.items():
                if animation.frame_ratio == None or (animation.frame_ratio and self.frame_number % animation.frame_ratio == 0):
                    self.animation_frames[name] = next(animation.generator)
                    if animation.duration is not None:
                        animation.duration -= 1
                        if animation.duration <= 0:
                            self.animations.pop(name)
                            self.animation_frames.pop(name)
            for name, frame in self.animation_frames.items():
                (x_coords, y_coords, tiles) = frame
                animation_console.tiles_rgb[x_coords[0]:x_coords[1], y_coords[0]:y_coords[1]] = tiles
            animation_console.blit(self.console, 0, 0, 0, 0,
                                   self.console.width, self.console.height)
            self.oldTime = time.time()
            self.oldFrame = animation_console
        else:
            self.oldFrame.blit(self.console, 0, 0, 0, 0,
                               self.console.width, self.console.height)
