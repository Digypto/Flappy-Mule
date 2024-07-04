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
        self.name = ""

    def update_score(self) -> None:
        """
        Increases the score by 1 point.
        """
        self.points += 1

    def update_name(self, name) -> None:
        """
        Adds a name to the user.
        """
        self.name = name

    def get_name(self) -> str:

        return self.name
    
    def get_score(self) -> int:

        return self.points
