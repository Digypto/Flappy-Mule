import pygame
from pygame.locals import *
import os
import random

WIDTH = 480
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Load the coin image
coin_image_path = f'{os.getcwd()}/assets/coin.png'
coin_image = pygame.image.load(coin_image_path)
coin_image = pygame.transform.scale(coin_image, (40, 40))  # Resize if needed
coin_image.convert_alpha()

class GameObject(pygame.sprite.Sprite):
    """
    A generic game object class that represents any moving object in the game.
    
    Attributes
    ----------
    image : pygame.Surface
        The image of the object.
    rect : pygame.Rect
        The rectangle representing the object's position and size.
    """
    def __init__(self, image_path: str, x: int, y: int) -> None:
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self) -> None:
        """
        Updates the object's position and removes it if it goes off-screen.
        """
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()


class Pipe(GameObject):
    """
    Represents a pipe obstacle in the game.
    """
    def __init__(self, position: str, height: int) -> None:
        y = height if position == "top" else HEIGHT - height
        super().__init__(f'{os.getcwd()}/assets/fence.png', WIDTH, y)
        if position == "top":
            self.rect.bottom = height
        else:
            self.rect.top = HEIGHT - height


class Coin(GameObject):
    """
    Represents a coin that the mule can collect in the game.
    """
    def __init__(self, x: int, y: int) -> None:
        super().__init__(f'{os.getcwd()}/assets/coin.png', x, y)


# Global sprite groups
all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
coins = pygame.sprite.Group()
last_pipe_time = 0
PIPE_INTERVAL = 1500

def create_pipe() -> None:
    """
    Creates a pair of top and bottom pipes with a gap between them,
    and adds them to the sprite groups.
    """
    global all_sprites, pipes, last_pipe_time

    gap_size = 200

    min_gap_position = 100
    max_gap_position = HEIGHT - 100 - gap_size
    gap_position = random.randint(min_gap_position, max_gap_position)

    top_pipe = Pipe("top", gap_position)
    bottom_pipe = Pipe("bottom", HEIGHT - gap_position - gap_size)

    all_sprites.add(top_pipe, bottom_pipe)
    pipes.add(top_pipe, bottom_pipe)


def create_coin() -> None:
    """
    Creates a coin at a random position that does not collide with pipes,
    and adds it to the sprite groups.
    """
    global all_sprites, coins

    x = WIDTH + 20
    valid_position = False
    y = 0

    while not valid_position:
        y = random.randint(50, HEIGHT - 50)
        valid_position = True

        for pipe in pipes:
            pipe_rect = pipe.rect.inflate(50, 50)
            if pipe_rect.collidepoint(x, y):
                valid_position = False
                break

    coin = Coin(x, y)
    all_sprites.add(coin)
    coins.add(coin)
