import pygame
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)


def draw_text_with_outline(screen: pygame.surface.Surface, text: str, font: pygame.font.Font, x: int, y: int) -> None:
    """
    Draws text with an outline on the screen.

    Parameters
    ----------
    text : str
        The text to be rendered.
    font : pygame.font.Font
        The font used to render the text.
    text_color : Tuple[int, int, int]
        The color of the text.
    outline_color : Tuple[int, int, int]
        The color of the text outline.
    x : int
        The x-coordinate where the text will be rendered.
    y : int
        The y-coordinate where the text will be rendered.
    """
    # Render the text with the outline color multiple times
    outline_positions = [(x-2, y-2), (x+2, y-2), (x-2, y+2), (x+2, y+2), (x-2, y), (x+2, y), (x, y-2), (x, y+2)]
    for pos in outline_positions:
        outline_text = font.render(text, True, BLACK)
        screen.blit(outline_text, pos)

    # Render the text with the main color
    main_text = font.render(text, True, WHITE)
    screen.blit(main_text, (x, y))

def draw_button(screen: pygame.surface.Surface, text: str, font: pygame.font.Font, x: int, y: int, width: int, height: int, inactive_color: tuple[int, int, int], active_color: tuple[int, int, int]) -> bool:
    """
    Draws a button on the screen and returns whether it is clicked.

    Parameters
    ----------
    text : str
        The text to be displayed on the button.
    font : pygame.font.Font
        The font used to render the button text.
    x : int
        The x-coordinate of the button's top-left corner.
    y : int
        The y-coordinate of the button's top-left corner.
    width : int
        The width of the button.
    height : int
        The height of the button.
    inactive_color : Tuple[int, int, int]
        The color of the button when it is not hovered over.
    active_color : Tuple[int, int, int]
        The color of the button when it is hovered over.

    Returns
    -------
    bool
        True if the button is clicked, otherwise False.
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    button_text = font.render(text, True, WHITE)
    screen.blit(button_text, (x + (width - button_text.get_width()) // 2, y + (height - button_text.get_height()) // 2))
    return False