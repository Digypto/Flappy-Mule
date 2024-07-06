import pygame
from pygame.locals import *


class Player(pygame.sprite.Sprite):
    """
    Represents the user in the game.

    Attributes
    ----------
    points : int
        The current score.
    name : str
        The name of the user (if asked)
    font : pygame.font.Font
        The font used to render the score.
    color : tuple[int, int, int]
        The color of the score text.
    outline_color : tuple[int, int, int]
        The color of the score text outline.
    """
    def __init__(self) -> None:
        super().__init__()
        self.points = -1
        self.point_multiplier = 1
        self.name = ""
        self.lives = 0

    def update_score(self) -> None:
        """
        Increases the score by 1 point multiplied by the multiplier.
        """
        self.points += 1 * self.point_multiplier

    def add_life(self) -> None:
        """
        Add a life to the user if powerup is collected.
        """
        self.lives += 1

    def remove_life(self) -> None:
        """
        Remove a life if a pipe is hit.
        """
        self.lives -= 1

    def update_name(self, name) -> None:
        """
        Adds a name to the user.
        """
        self.name = name

    def get_name(self) -> str:

        return self.name
    
    def get_score(self) -> int:

        return self.points
    
    def activate_double_points(self):
        self.point_multiplier = 2

    def deactivate_double_points(self):
        self.point_multiplier = 1
