import pygame
from pygame.locals import *
from db.db_operations import save_user, get_users
from db.db_connection import get_db_connection
import hashlib
from player import Player

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
    data = get_users(client)
    player = Player()
    for json in data:
        user = json["user"]
        db_password = json["password"]
        if username == user and hashed_password == db_password:
            player.update_name(username)
            return True, player
        else:
            return False, None
        
def validate_registration(username: str, password: str, password_again: str) -> bool:
    sha256 = hashlib.sha256()
    encoded_password = password.encode()
    sha256.update(encoded_password)
    hashed_password = sha256.hexdigest()
    data = get_users(client)
    player = Player()
    return_bool = False
    return_text = None
    for json in data:
        user = json["user"]
        if username == user:
            return_bool = False
            return_text = "Username already taken."
            break
        if password.lower() != password_again.lower():
            return_bool = False
            return_text = "The passwords do not match."
            break
        if len(password.lower()) < 5:
            return_bool = False
            return_text = "The passwords needs to contain at least 5 characters."
            break
        player.update_name(username)
        save_user(client, username, hashed_password)
        return_bool = True
        return_text = "Registration successful."

    return return_bool, return_text, player
    