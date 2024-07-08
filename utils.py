import pygame
from pygame.locals import *
from db.db_operations import save_user
from db.db_connection import get_db_connection
import hashlib

client = get_db_connection()

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

def validate_sign_in(username: str, password: str) -> bool:
    sha256 = hashlib.sha256()
    encoded_password = password.encode()
    sha256.update(encoded_password)
    hashed_password = sha256.hexdigest()
    print(username, password, encoded_password, hashed_password)
    #save_user(client, username, hashed_password)
    