import pygame
from pygame.locals import *
import os

from screen_manager import ScreenManager

pygame.init()
pygame.mixer.init()
pygame.font.init()  # Initialize the font module


WIDTH = 480
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Mule")

# Load custom font from Google Fonts
font_path = f'{os.getcwd()}/assets/BebasNeue-Regular.ttf'

# Initialize ScreenManager
screen_manager = ScreenManager(screen, font_path)



if __name__ == "__main__":
    screen_manager.main_menu()
    while True:
        screen_manager.run_game()


pygame.quit()
exit()