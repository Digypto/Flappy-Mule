import pygame
from pygame.locals import *
import os
import random


WIDTH = 480
HEIGHT = 500

class Pipe(pygame.sprite.Sprite):
    """
    Represents a pipe obstacle in the game.

    Attributes
    ----------
    image : pygame.Surface
        The image of the pipe.
    rect : pygame.Rect
        The rectangle representing the pipe's position and size.
    """
    def __init__(self, position: str, height: int) -> None:
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/assets/fence.png')
        self.rect = self.image.get_rect()
        if position == "top":
            self.rect.bottom = height
        else:
            self.rect.top = HEIGHT - height
        self.rect.x = WIDTH

    def update(self) -> None:
        """
        Updates the pipe's position and removes it if it goes off-screen.
        """
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()




def create_pipe() -> None:
    """
    Creates a pair of top and bottom pipes with a gap between them,
    and adds them to the sprite groups.
    """
    global all_sprites, pipes, last_pipe_time

    # Define the gap size between top and bottom pipes (adjust if the game is too easy or hard)
    gap_size = 200

    # Randomly determine the position of the gap
    min_gap_position = 100
    max_gap_position = HEIGHT - 100 - gap_size
    gap_position = random.randint(min_gap_position, max_gap_position)

    top_pipe = Pipe("top", gap_position)
    bottom_pipe = Pipe("bottom", HEIGHT - gap_position - gap_size)

    # Add the pipes to the sprite groups
    all_sprites.add(top_pipe, bottom_pipe)
    pipes.add(top_pipe, bottom_pipe)