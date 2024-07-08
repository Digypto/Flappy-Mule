import pygame
from pygame.locals import *
from db.db_operations import save_score, get_high_scores, get_worst_score_in_db

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

def validate_sign_in() -> bool:
    pass