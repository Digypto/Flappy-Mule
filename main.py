import pygame
from pygame.locals import *
import os
import ctypes
import subprocess

from db.db_operations import save_score, get_high_scores, get_worst_score_in_db
from db.db_connection import get_db_connection, retrieve_db_credentials
from utils import play_coin_collision_sound, play_collision_sound


from player import Player
from game_objects import Mule, all_sprites, pipes, coins, last_pipe_time, PIPE_INTERVAL, create_coin, create_pipe
from drawing import draw_button, draw_text_with_outline

# Initialize pygame
credential_dict = retrieve_db_credentials()
user = credential_dict.get("user")
password = credential_dict.get("password")
host = credential_dict.get("host")
appname = credential_dict.get("appname")
client = get_db_connection(user, password, host, appname)
pygame.init()
pygame.mixer.init()
pygame.font.init()  # Initialize the font module

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

WIDTH = 480
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Mule")
clock = pygame.time.Clock()

bg = pygame.image.load(f'{os.getcwd()}/assets/background.png').convert_alpha()

# Load custom font from Google Fonts
font_path = f'{os.getcwd()}/assets/BebasNeue-Regular.ttf'
font = pygame.font.Font(font_path, 160)
button_font = pygame.font.Font(font_path, 48)  # Smaller font for the button
score_font = pygame.font.Font(font_path, 120)  # Font for the score
leaderboard_font = pygame.font.Font(font_path, 28)




def ask_username_screen(player: Player):

    score_label = "Score: " + str(player.points)
    score_x = WIDTH // 3 - font.size(str(player.points))[1] // 2
    score_y = HEIGHT // 2 - font.size(score_label)[1] // 2 - 150
    draw_text_with_outline(score_label, score_font, score_x, score_y)

    congratulations_text = "Wow, you are in the top 5 of the biggest mules!"
    text_x = 25
    text_y = score_y + 175
    draw_text_with_outline(congratulations_text, leaderboard_font, text_x, text_y)


    username_label = "Enter a username to get on the leaderboard."
    username_x = 25
    username_y = text_y + 40 # Position below the former text
    draw_text_with_outline(username_label, leaderboard_font, username_x, username_y)



    base_font = pygame.font.Font(None, 32)
    user_text = ''

    # Create input rectangle
    input_box_y = username_y + 50
    input_rect = pygame.Rect(WIDTH // 2 - 175, input_box_y, 200, 50)

    # Draw "No" button
    no_button_x = WIDTH // 2 - 115
    no_button_y = input_box_y + 75
    no_button_width = 200
    no_button_height = 50

    color_active = pygame.Color(((200,200,200))) #light gray
    color_passive = pygame.Color('black')
    color = color_passive

    active = False


    while True:
        #yes_button = draw_button("Yes", button_font, yes_x, yes_y, yes_width, yes_height, BLACK, LIGHT_GRAY)
        no_button = draw_button("No thanks", button_font, no_button_x, no_button_y, no_button_width, no_button_height, BLACK, LIGHT_GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if no_button:
                main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        try:
                            ctypes.windll.user32.MessageBoxW(0, "Score saved!", "Popup", 0)
                        except AttributeError:
                            applescript = """
                                display dialog "Score saved!" ¬
                                with title "Popup" ¬
                                buttons {"OK"}
                                """
                            subprocess.call("osascript -e '{}'".format(applescript), shell=True)
                        player.update_name(user_text)
                        save_score(client, player.points, player.name)  # Save the score to the database
                        user_text = ''
                        main_menu()
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

        if active:
            color = color_active
        else:
            color = color_passive

        pygame.draw.rect(screen, color, input_rect)

        if user_text == '':
            text_surface = base_font.render("The name of the awesome mule", True, (198, 215, 255))  # Lighter color for placeholder
        else:
            text_surface = base_font.render(user_text, True, (255, 255, 255))  # White color for user input
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        input_rect.w = max(200, text_surface.get_width() + 10)


def game_over_screen(player: Player) -> bool:
    """
    Displays the game over screen with the final score and a "Play Again" button.

    Parameters
    ----------
    score : Score
        The final score of the game.

    Returns
    -------
    bool
        True if the player wants to play again, otherwise False.
    """

    game_over_text = "FOOO"
    text_x = WIDTH // 2 - font.size(game_over_text)[0] // 2
    text_y = HEIGHT // 2 - font.size(game_over_text)[1] // 2 - 150
    draw_text_with_outline(game_over_text, font, text_x, text_y)

    # Render the score below the "FOOO" text
    score_label = "Score: " + str(player.points)
    score_x = WIDTH // 3 - font.size(str(player.points))[1] // 2 + 25
    score_y = text_y + 175 # Position below "FOOO" text
    draw_text_with_outline(score_label, score_font, score_x, score_y)

    death_time = pygame.time.get_ticks() # record the time when the mule dies


    # Draw "Play Again" button
    button_x = WIDTH // 2 - 100
    button_y = score_y + 150
    button_width = 200
    button_height = 70

    # Draw "Main menu" button
    menu_button_x = WIDTH // 2 - 100
    menu_button_y = button_y + 75
    menu_button_width = 200
    menu_button_height = 70


    while True:
        play_again = draw_button("Play Again", button_font, button_x, button_y, button_width, button_height, BLACK, LIGHT_GRAY)
        main_menu_button = draw_button("Main menu", button_font, menu_button_x, menu_button_y, menu_button_width, menu_button_height, BLACK, LIGHT_GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time - death_time >= 2000:  # check if 2 seconds have passed
                        run_game()
            if play_again:
                run_game()
            if main_menu_button:
                main_menu()


def display_leaderboard():
    leaderboard_font = pygame.font.Font(font_path, 36)
    title_font = pygame.font.Font(font_path, 72)
    back_button_font = pygame.font.Font(font_path, 36)

    high_scores_cursor = get_high_scores(client)
    high_scores = list(high_scores_cursor)

    running = True
    while running:
        screen.blit(bg, (0,0))

        # Draw title
        leaderboard_title = "Leaderboard"
        title_x = WIDTH // 2 - title_font.size(leaderboard_title)[0] // 2
        title_y = HEIGHT // 20
        draw_text_with_outline(leaderboard_title, title_font, title_x, title_y)

        # Draw scores
        for i, score_doc in enumerate(high_scores):
            score_value = score_doc.get('score')  # Accessing the 'score' field from the document
            user_name = score_doc.get('user')
            score_text = f"{i + 1}. {user_name}: {score_value}"
            text_x = WIDTH // 2 // 2
            text_y = title_y + (i + 2) * 50
            draw_text_with_outline(score_text, leaderboard_font, text_x, text_y)
        
        # Draw "Back" button
        back_button_x = WIDTH // 2 - 100
        back_button_y = HEIGHT - 100
        back_button_width = 200
        back_button_height = 70
        back = draw_button("Back", back_button_font, back_button_x, back_button_y, back_button_width, back_button_height, BLACK, LIGHT_GRAY)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if back:
                main_menu()
            
def main_menu():
    """
    Displays the main menu and waits for the user to click the "Play" button.
    """

    button_x = WIDTH // 2 - 125
    button_y = HEIGHT // 2 - 35
    button_width = 200
    button_height = 70
    
    while True:
        screen.blit(bg, (0, 0))

        # Draw title
        flappy_title = "Flappy Mule"
        title_font = pygame.font.Font(font_path, 90)
        flappy_x = WIDTH // 2 - title_font.size(flappy_title)[0] // 2
        flappy_y = HEIGHT // 6
        draw_text_with_outline(flappy_title, title_font, flappy_x, flappy_y)


        play = draw_button("Play", button_font, button_x, button_y, button_width + 50, button_height, BLACK, LIGHT_GRAY)
        leaderboard = draw_button("Leaderboard", button_font, button_x, button_y + 100, button_width + 50, button_height, BLACK, LIGHT_GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if play:
                run_game()
            if leaderboard:
                display_leaderboard()

        pygame.display.flip()


def run_game() -> bool:
    """
    Runs the main game loop, updating and rendering all elements.

    Returns
    -------
    bool
        True if the player wants to play again, otherwise False.
    """
    global all_sprites, pipes, coins, last_pipe_time

    all_sprites.empty()  # Clear the sprite groups
    pipes.empty()
    coins.empty()

    mule = Mule()
    player = Player()
    all_sprites.add(mule)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mule.jump()
            elif event.type == pygame.QUIT:
                running = False
                return False
            
        screen.blit(bg, (0, 0))

        all_sprites.update()

        # Pipes at controlled intervals
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_INTERVAL:
            create_pipe()
            create_coin()
            last_pipe_time = current_time
            player.update_score()

        pipe_collision = pygame.sprite.spritecollide(mule, pipes, False)
        if pipe_collision:
            play_collision_sound()
            running = False
        
        coin_collision = pygame.sprite.spritecollide(mule, coins, True)  # Detect coin collision
        if coin_collision:
            play_coin_collision_sound()
            player.points += 1  # Increase score by 1 for each coin collected

        all_sprites.draw(screen)
        if running and player.points >= 0:
            draw_text_with_outline(str(player.points), pygame.font.Font(font_path, 48), WIDTH // 2, HEIGHT // 7)
        pygame.display.flip()
        clock.tick(60)


    if player.points > get_worst_score_in_db(client)[0] or get_worst_score_in_db(client)[1] < 5: #check if there are under 5 entries in db or the user is better than the worst score in db
        return ask_username_screen(player)
    if get_worst_score_in_db(client)[0] >= player.points:
        return game_over_screen(player)


if __name__ == "__main__":
    main_menu()
    while True:
        run_game()


pygame.quit()
exit()