import pygame
from pygame.locals import *
import os

def crop_image(image: pygame.Surface) -> pygame.Surface:
    """
    Crops the transparent parts of an image.

    Parameters
    ----------
    image : pygame.Surface
        The image to be cropped.

    Returns
    -------
    pygame.Surface
        The cropped image.
    """
    rect = image.get_bounding_rect()
    cropped_image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cropped_image.blit(image, (0, 0), rect)  # Identifies the transparent parts and removes them
    return cropped_image

def play_collision_sound() -> None:
    """
    Plays a sound effect when a collision occurs.
    """
    mule_sound = f'{os.getcwd()}/assets/mule.mp3'
    pygame.mixer.init()
    pygame.mixer.music.load(mule_sound)
    pygame.mixer.music.play()

def play_coin_collision_sound() -> None:
    """
    Plays a sound effect when user touches a coin.
    """
    omnom_sound = f'{os.getcwd()}/assets/omnom.mp3'
    pygame.mixer.init()
    pygame.mixer.music.load(omnom_sound)
    pygame.mixer.music.play()