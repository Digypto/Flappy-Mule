import pygame
from pygame.locals import *
import os

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