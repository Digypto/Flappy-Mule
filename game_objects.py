import pygame
from pygame.locals import *
import os
import random
from utils import crop_image

WIDTH = 480
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))


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
    def __init__(self, image: pygame.image, x: int, y: int) -> None:
        super().__init__()
        self.image = image
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

class Mule(pygame.sprite.Sprite):
    """
    Represents the mule that the player controls.

    Attributes
    ----------
    image : pygame.Surface
        The image of the mule.
    rect : pygame.Rect
        The rectangle representing the mule's position and size.
    change_y : int
        The change in the mule's y-coordinate (vertical velocity).
    """
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/assets/mule.png')
        self.image = pygame.transform.scale(self.image, (80, 80))  # Resizing
        self.image.convert_alpha()
        self.image = crop_image(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT // 2
        self.change_y = 0

    def update(self) -> None:
        """
        Updates the mule's position and handles vertical movement.
        """
        self.change_y += 1
        self.rect.y += self.change_y
        if self.rect.y >= HEIGHT - 50:
            self.rect.y = HEIGHT - 50
            self.change_y = 0
        if self.rect.y <= 0:
            self.rect.y = 0
            self.change_y = 0

    def jump(self) -> None:
        """
        Makes the mule jump by setting its vertical velocity.
        """
        self.change_y = -10            


class Pipe(GameObject):
    """
    Represents a pipe obstacle in the game.
    """
    def __init__(self, position: str, height: int) -> None:
        y = height if position == "top" else HEIGHT - height
        image = pygame.image.load(f'{os.getcwd()}/assets/fence.png')
        super().__init__(image, WIDTH, y)
        if position == "top":
            self.rect.bottom = height
        else:
            self.rect.top = HEIGHT - height


class Coin(GameObject):
    """
    Represents a coin that the mule can collect in the game.
    """
    def __init__(self, x: int, y: int) -> None:
        image = pygame.image.load(f'{os.getcwd()}/assets/coin.png')
        super().__init__(image, x, y)

class PowerUp(GameObject):
    """
    Represents a powerup that the mule can collect in the game.
    """
    def __init__(self, x: int, y: int) -> None:
        selected_powerup = self.select_random_powerup()
        image = pygame.image.load(f'{os.getcwd()}/assets/{selected_powerup}.png')
        image = pygame.transform.scale(image, (250, 250))  # Resizing
        image.convert_alpha()
        image = crop_image(image)
        super().__init__(image, x, y)
        self.start_time = None
        self.active = False

    def select_random_powerup(self) -> str:
        powerups_dict = {1: "double_points", 2: "extra_life"}
        select_random_powerup = random.randint(1,2)
        selected_powerup = powerups_dict.get(select_random_powerup)
        return selected_powerup

    def activate(self, current_time):
        self.start_time = current_time
        self.active = True

    def is_active(self, current_time):
        if self.active and current_time - self.start_time > POWERUP_DURATION:
            self.active = False
        return self.active


# Global sprite groups
all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
coins = pygame.sprite.Group()
powerups = pygame.sprite.Group()
last_pipe_time = 0
PIPE_INTERVAL = 1500
POWERUP_DURATION = 5000

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

    valid_position = False
    y = 0

    while not valid_position:
        y = random.randint(25, HEIGHT - 25)
        x = random.randint(100, WIDTH)
        valid_position = True

        for pipe in pipes:
            pipe_rect = pipe.rect.inflate(50, 50)
            if pipe_rect.collidepoint(x, y):
                valid_position = False
                break

    coin = Coin(x, y)
    all_sprites.add(coin)
    coins.add(coin)

def create_powerup() -> None:
    """
    Creates a coin at a random position that does not collide with pipes,
    and adds it to the sprite groups.
    """
    global all_sprites, powerups

    valid_position = False
    y = 0

    while not valid_position:
        y = random.randint(25, HEIGHT - 25)
        x = random.randint(100, WIDTH)
        valid_position = True

        for pipe in pipes:
            pipe_rect = pipe.rect.inflate(50, 50)
            if pipe_rect.collidepoint(x, y):
                valid_position = False
                break

    powerup = PowerUp(x, y)
    all_sprites.add(powerup)
    powerups.add(powerup)
