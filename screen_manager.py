import pygame
import os
import ctypes
import subprocess

from db.db_operations import save_score, get_high_scores, get_worst_score_in_db, update_user_lifetime_score, update_user_latest_sign_in
from db.db_connection import get_db_connection
from sound_manager import play_coin_collision_sound, play_collision_sound, play_powerup_collision_sound
from drawing import draw_text_with_outline, draw_button, draw_rect
from utils import validate_sign_in, validate_registration, crop_image
from data_processing import database_to_dataframe

from player import Player
from game_objects import Mule, all_sprites, pipes, coins, powerups, last_pipe_time, PIPE_INTERVAL, create_coin, create_pipe, create_powerup

client = get_db_connection()

clock = pygame.time.Clock()

WIDTH = 480
HEIGHT = 500

bg = pygame.image.load(f'{os.getcwd()}/assets/background.png').convert_alpha()


class ScreenManager:
    def __init__(self, screen, font_path):
        self.screen = screen
        self.font_path = font_path
        self.player = Player()
        self.load_fonts()
        self.achievements = Achievements(screen, self, self.font_path, self.leaderboard_font, self.button_font)

    def load_fonts(self):
        self.base_font = pygame.font.Font(self.font_path, 32)
        self.register_font = pygame.font.Font(self.font_path, 16)
        self.leaderboard_font = pygame.font.Font(self.font_path, 36)
        self.congratulations_font = pygame.font.Font(self.font_path, 28)
        self.title_font = pygame.font.Font(self.font_path, 90)
        self.game_over_font = pygame.font.Font(self.font_path, 160)
        self.button_font = pygame.font.Font(self.font_path, 48)
        self.score_font = pygame.font.Font(self.font_path, 120)

    def ask_username_screen(self):
        score_label = "Score: " + str(self.player.points)
        score_x = WIDTH // 3 - self.score_font.size(str(self.player.points))[1] // 2
        score_y = HEIGHT // 2 - self.score_font.size(score_label)[1] // 2 - 150
        draw_text_with_outline(self.screen, score_label, self.score_font, score_x, score_y)

        congratulations_text = "Wow, you are in the top 5 of the biggest mules!"
        text_x = 25
        text_y = score_y + 175
        draw_text_with_outline(self.screen, congratulations_text, self.congratulations_font, text_x, text_y)

        username_label = "Enter a username to get on the leaderboard."
        username_x = 25
        username_y = text_y + 40
        draw_text_with_outline(self.screen, username_label, self.congratulations_font, username_x, username_y)


        input_box_y = username_y + 50
        input_rect = pygame.Rect(WIDTH // 2 - 175, input_box_y, 200, 50)

        no_button_x = WIDTH // 2 - 115
        no_button_y = input_box_y + 75
        no_button_width = 200
        no_button_height = 50

        color_active = pygame.Color((200, 200, 200))
        color_passive = pygame.Color('black')
        color = color_passive

        active = False
        user_text = ''

        while True:
            no_button = draw_button(self.screen, "No thanks", self.button_font, no_button_x, no_button_y, no_button_width, no_button_height, (0, 0, 0), (200, 200, 200))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if no_button:
                    self.player.reset_points()
                    self.main_menu()
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
                            self.player.update_name(user_text)
                            save_score(client, self.player.points, self.player.name)  # Save the score to the database
                            user_text = ''
                            self.player.reset_points()
                            self.main_menu()
                        if event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                        else:
                            user_text += event.unicode

            if active:
                color = color_active
            else:
                color = color_passive

            pygame.draw.rect(self.screen, color, input_rect)

            if user_text == '':
                text_surface = self.base_font.render("The name of the awesome mule", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(user_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

            input_rect.w = max(200, text_surface.get_width() + 10)


    def game_over_screen(self):
        game_over_text = "FOOO"
        text_x = WIDTH // 2 - self.game_over_font.size(game_over_text)[0] // 2
        text_y = HEIGHT // 2 - self.game_over_font.size(game_over_text)[1] // 2 - 150
        draw_text_with_outline(self.screen, game_over_text, self.game_over_font, text_x, text_y)

        score_label = "Score: " + str(self.player.points)
        score_x = WIDTH // 3 - self.score_font.size(str(self.player.points))[1] // 2
        score_y = text_y + 175
        draw_text_with_outline(self.screen, score_label, self.score_font, score_x, score_y)

        death_time = pygame.time.get_ticks()

        button_x = WIDTH // 2 - 100
        button_y = score_y + 150
        button_width = 200
        button_height = 70

        menu_button_x = WIDTH // 2 - 100
        menu_button_y = button_y + 75
        menu_button_width = 200
        menu_button_height = 70

        self.player.reset_points()

        while True:
            play_again = draw_button(self.screen, "Play Again", self.button_font, button_x, button_y, button_width, button_height, (0, 0, 0), (200, 200, 200))
            main_menu_button = draw_button(self.screen, "Main menu", self.button_font, menu_button_x, menu_button_y, menu_button_width, menu_button_height, (0, 0, 0), (200, 200, 200))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        current_time = pygame.time.get_ticks()
                        if current_time - death_time >= 2000:
                            self.run_game()
                if play_again:
                    self.run_game()
                if main_menu_button:
                    self.main_menu()


    def display_leaderboard(self):
        high_scores_cursor = get_high_scores(client)
        high_scores = list(high_scores_cursor)
        database_to_dataframe("scores")

        running = True
        while running:
            self.screen.blit(bg, (0,0))

            leaderboard_title = "Leaderboard"
            title_x = WIDTH // 2 - self.title_font.size(leaderboard_title)[0] // 2
            title_y = HEIGHT // 20
            draw_text_with_outline(self.screen, leaderboard_title, self.title_font, title_x, title_y)

            for i, score_doc in enumerate(high_scores):
                score_value = score_doc.get('score')
                user_name = score_doc.get('user')
                score_text = f"{i + 1}. {user_name}: {score_value}"
                text_x = WIDTH // 2 // 2
                text_y = title_y + (i + 2) * 50
                draw_text_with_outline(self.screen, score_text, self.leaderboard_font, text_x, text_y)

            back_button_x = WIDTH // 2 - 100
            back_button_y = HEIGHT - 100
            back_button_width = 200
            back_button_height = 70
            back = draw_button(self.screen, "Back", self.button_font, back_button_x, back_button_y, back_button_width, back_button_height, (0, 0, 0), (200, 200, 200))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if back:
                    self.main_menu()

    def main_menu(self):
        button_x = WIDTH // 2 - 125
        button_y = HEIGHT // 2 - 35
        button_width = 200
        button_height = 70

        while True:
            self.screen.blit(bg, (0, 0))

            flappy_title = "Flappy Mule"
            flappy_x = WIDTH // 2 - self.title_font.size(flappy_title)[0] // 2
            flappy_y = HEIGHT // 6
            draw_text_with_outline(self.screen, flappy_title, self.title_font, flappy_x, flappy_y)

            play = draw_button(self.screen, "Play", self.button_font, button_x, button_y, button_width + 50, button_height, (0, 0, 0), (200, 200, 200))
            leaderboard = draw_button(self.screen, "Leaderboard", self.leaderboard_font, button_x, button_y + 100, button_width + 50, button_height, (0, 0, 0), (200, 200, 200))
            achievements = draw_button(self.screen, "Achievements", self.button_font, button_x, button_y + 200, button_width + 50, button_height, (0, 0, 0), (200, 200, 200))
            if self.player.get_name():
                draw_text_with_outline(self.screen, f'User: {self.player.get_name()}', self.congratulations_font, 5, 5)
            if not self.player.get_name():
                sign_in = draw_button(self.screen, "Sign in", self.base_font, 5, 5, 100, 40, (0, 0, 0), (200, 200, 200))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if play:
                    self.run_game()
                if leaderboard:
                    self.display_leaderboard()
                if achievements:
                    self.achievements.achievements_screen("Basic achievements")
                if not self.player.get_name():
                    if sign_in:
                        self.sign_in_screen()

            pygame.display.flip()

    def sign_in_or_continue_as_guest(self):
        button_x = WIDTH // 2 - 125
        button_y = HEIGHT // 2 - 35
        button_width = 200
        button_height = 70

        while True:
            self.screen.blit(bg, (0, 0))

            flappy_title = "Flappy Mule"
            flappy_x = WIDTH // 2 - self.title_font.size(flappy_title)[0] // 2
            flappy_y = HEIGHT // 6
            draw_text_with_outline(self.screen, flappy_title, self.title_font, flappy_x, flappy_y)

            sign_in = draw_button(self.screen, "Sign in", self.button_font, button_x - 50, button_y, button_width + 150, button_height, (0, 0, 0), (200, 200, 200))
            guest = draw_button(self.screen, "Continue as a guest", self.button_font, button_x - 50, button_y + 100, button_width + 150, button_height, (0, 0, 0), (200, 200, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if sign_in:
                    self.sign_in_screen()
                if guest:
                    self.main_menu()

            pygame.display.flip()
    
    def register_screen(self):
        button_x = WIDTH // 2 - 100
        button_y = HEIGHT - 150
        button_width = 200
        button_height = 70

        color_active = pygame.Color((200, 200, 200))
        color_passive = pygame.Color('black')
        color_username = color_passive
        color_password = color_passive
        color_password_again = color_passive
        username_box_y = 50
        username_rect = pygame.Rect(WIDTH // 2 - 100, username_box_y, 200, 50)
        password_box_y = username_box_y + 75
        password_rect = pygame.Rect(WIDTH // 2 - 100, password_box_y, 200, 50)
        password_again_box_y = password_box_y + 75
        password_again_rect = pygame.Rect(WIDTH // 2 - 100, password_again_box_y, 200, 50)

        username_active = False
        username_text = ''

        password_active = False
        password_text = ''

        password_again_active = False
        password_again_text = ''

        while True:
            self.screen.blit(bg, (0, 0))

            back = draw_button(self.screen, "Back", self.button_font, button_x, button_y, button_width, button_height, (0, 0, 0), (200, 200, 200))
            register = draw_button(self.screen, "Register", self.button_font, button_x, password_again_box_y + 75, button_width, button_height, (0, 0, 0), (200, 200, 200))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if back:
                    self.sign_in_screen()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if username_rect.collidepoint(event.pos):
                        username_active = True
                    else:
                        username_active = False
                    if password_rect.collidepoint(event.pos):
                        password_active = True
                    else:
                        password_active = False
                    if password_again_rect.collidepoint(event.pos):
                        password_again_active = True
                    else:
                        password_again_active = False
                if event.type == pygame.KEYDOWN:
                    if username_active:
                        if event.key == pygame.K_BACKSPACE:
                            username_text = username_text[:-1]
                        else:
                            username_text += event.unicode
                    if password_active:
                        if event.key == pygame.K_BACKSPACE:
                            password_text = password_text[:-1]
                        else:
                            password_text += event.unicode
                    if password_again_active:
                        if event.key == pygame.K_BACKSPACE:
                            password_again_text = password_again_text[:-1]
                        else:
                            password_again_text += event.unicode    
                if register:
                    validation = validate_registration(username_text, password_text, password_again_text)
                    validation_bool = validation[0]
                    validation__text = validation[1]
                    if validation_bool:
                        try:
                            ctypes.windll.user32.MessageBoxW(0, validation__text, "Popup", 0)
                        except AttributeError:
                            applescript = """
                                display dialog "Registration successful." ¬
                                with title "Popup" ¬
                                buttons {"OK"}
                                """
                            subprocess.call("osascript -e '{}'".format(applescript), shell=True) 
                        self.player = validation[2]
                        self.main_menu()
                    if not validation_bool:
                        try:
                            ctypes.windll.user32.MessageBoxW(0, validation__text, "Popup", 0)
                        except AttributeError:
                            applescript = """
                                display dialog "Wrong username or password." ¬
                                with title "Popup" ¬
                                buttons {"OK"}
                                """
                            subprocess.call("osascript -e '{}'".format(applescript), shell=True) #TODO input validation_error_text to applescipt
                    username_text = ''
                    password_text = ''
                    password_again_text = ''
            if username_active:
                color_username = color_active
            else:
                color_username = color_passive
            if password_active:
                color_password = color_active
            else:
                color_password = color_passive
            if password_again_active:
                color_password_again = color_active
            else:
                color_password_again = color_passive

            pygame.draw.rect(self.screen, color_username, username_rect)

            if username_text == '':
                text_surface = self.base_font.render("Username", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(username_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (username_rect.x + 5, username_rect.y + 5))

            username_rect.w = max(200, text_surface.get_width() + 10)

            pygame.draw.rect(self.screen, color_password, password_rect)

            if password_text == '':
                text_surface = self.base_font.render("Password", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(password_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (password_rect.x + 5, password_rect.y + 5))

            password_rect.w = max(200, text_surface.get_width() + 10)

            pygame.draw.rect(self.screen, color_password_again, password_again_rect)

            if password_again_text == '':
                text_surface = self.base_font.render("Password again", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(password_again_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (password_again_rect.x + 5, password_again_rect.y + 5))

            password_again_rect.w = max(200, text_surface.get_width() + 10)

            pygame.display.flip()


    def sign_in_screen(self):
        button_x = WIDTH // 2 - 100
        button_y = HEIGHT - 100
        button_width = 200
        button_height = 70

        color_active = pygame.Color((200, 200, 200))
        color_passive = pygame.Color('black')
        color_username = color_passive
        color_password = color_passive
        username_box_y = 150
        username_rect = pygame.Rect(WIDTH // 2 - 100, username_box_y, 200, 50)
        password_box_y = username_box_y + 75
        password_rect = pygame.Rect(WIDTH // 2 - 100, password_box_y, 200, 50)

        username_active = False
        username_text = ''

        password_active = False
        password_text = ''

        while True:
            self.screen.blit(bg, (0, 0))

            back = draw_button(self.screen, "Back", self.button_font, button_x, button_y, button_width, button_height, (0, 0, 0), (200, 200, 200))
            register = draw_button(self.screen, "Don't have an account? Register here", self.register_font, 5, 5, 215, 30, (0, 0, 0), (200, 200, 200))
            sign_in = draw_button(self.screen, "Sign in", self.button_font, button_x, password_box_y + 75, button_width, button_height, (0, 0, 0), (200, 200, 200))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if register:
                    self.register_screen()
                if back:
                    self.sign_in_or_continue_as_guest()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if username_rect.collidepoint(event.pos):
                        username_active = True
                    else:
                        username_active = False
                    if password_rect.collidepoint(event.pos):
                        password_active = True
                    else:
                        password_active = False
                if event.type == pygame.KEYDOWN:
                    if username_active:
                        if event.key == pygame.K_BACKSPACE:
                            username_text = username_text[:-1]
                        else:
                            username_text += event.unicode
                    if password_active:
                        if event.key == pygame.K_BACKSPACE:
                            password_text = password_text[:-1]
                        else:
                            password_text += event.unicode
                if sign_in:
                    validation_bool = validate_sign_in(username_text, password_text)
                    if validation_bool[0]:
                        self.player = validation_bool[1]
                        update_user_latest_sign_in(client, "jee")
                        self.main_menu()
                    if not validation_bool[0]:
                        try:
                            ctypes.windll.user32.MessageBoxW(0, "Wrong username or password.", "Popup", 0)
                        except AttributeError:
                            applescript = """
                                display dialog "Wrong username or password." ¬
                                with title "Popup" ¬
                                buttons {"OK"}
                                """
                            subprocess.call("osascript -e '{}'".format(applescript), shell=True)
                    username_text = ''
                    password_text = ''
            if username_active:
                color_username = color_active
            else:
                color_username = color_passive
            if password_active:
                color_password = color_active
            else:
                color_password = color_passive

            pygame.draw.rect(self.screen, color_username, username_rect)

            if username_text == '':
                text_surface = self.base_font.render("Username", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(username_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (username_rect.x + 5, username_rect.y + 5))

            username_rect.w = max(200, text_surface.get_width() + 10)

            pygame.draw.rect(self.screen, color_password, password_rect)

            if password_text == '':
                text_surface = self.base_font.render("Password", True, (198, 215, 255))
            else:
                text_surface = self.base_font.render(password_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (password_rect.x + 5, password_rect.y + 5))

            password_rect.w = max(200, text_surface.get_width() + 10)

            pygame.display.flip()

    def run_game(self) -> bool:
        """
        Runs the main game loop, updating and rendering all elements.

        Returns
        -------
        bool
            True if the player wants to play again, otherwise False.
        """
        global all_sprites, pipes, coins, powerups, last_pipe_time

        all_sprites.empty()  # Clear the sprite groups
        pipes.empty()
        coins.empty()
        powerups.empty()

        mule = Mule()
        player = self.player
        all_sprites.add(mule)
        powerup = None

        running = True
        collision_handled = False
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
                
            self.screen.blit(bg, (0, 0))

            all_sprites.update()

            # Pipes at controlled intervals
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > PIPE_INTERVAL:
                create_pipe()
                create_coin()
                last_pipe_time = current_time
                player.update_score()
            if current_time % 10000 < 15: #Create a power up every 10 seconds
                create_powerup()
            pipe_collision = pygame.sprite.spritecollide(mule, pipes, False)
            if pipe_collision and not collision_handled:
                play_collision_sound()
                if player.lives == 0:
                    running = False
                else:
                    player.remove_life()
                    collision_handled = True
            
            coin_collision = pygame.sprite.spritecollide(mule, coins, True)  # Detect coin collision
            if coin_collision:
                play_coin_collision_sound()
                player.update_score()
            
            powerup_collision = pygame.sprite.spritecollide(mule, powerups, True)  # Detect powerup collision
            if powerup_collision:
                play_powerup_collision_sound()
                for powerup in powerup_collision:
                    powerup_collected = powerup.get_selected_powerup()
                if powerup_collected == 'double_points':
                    powerup.activate(current_time)
                    player.activate_double_points()
                elif powerup_collected == 'extra_life':
                    player.add_life() 

            if powerup and not powerup.is_active(current_time):
                player.deactivate_double_points()

            if not pipe_collision:
                collision_handled = False

            all_sprites.draw(self.screen)
            if running and player.points >= 0 and player.lives >= 0:
                draw_text_with_outline(self.screen, f'Lives: {str(player.lives)}', pygame.font.Font(self.font_path, 48), 10, 10)
                draw_text_with_outline(self.screen, str(player.points), pygame.font.Font(self.font_path, 48), WIDTH // 2, HEIGHT // 7)
            pygame.display.flip()
            clock.tick(60)


        if player.points > get_worst_score_in_db(client)[0] or get_worst_score_in_db(client)[1] < 5: #check if there are under 5 entries in db or the user is better than the worst score in db
            if self.player.get_name():
                save_score(client, player.points, player.name)
                update_user_lifetime_score(client, self.player.name, self.player.points)
                try:
                    ctypes.windll.user32.MessageBoxW(0, "Your score was saved on the leaderboard", "Popup", 0)
                except AttributeError:
                    applescript = """
                        display dialog "Your score was saved on the leaderboard" ¬
                        with title "Popup" ¬
                        buttons {"OK"}
                        """
                    subprocess.call("osascript -e '{}'".format(applescript), shell=True)
            else:
                return self.ask_username_screen()
        if get_worst_score_in_db(client)[0] >= player.points:
            update_user_lifetime_score(client, self.player.name, self.player.points)
            return self.game_over_screen()



class Achievements():
    def __init__(self, screen, screen_manager, font_path, title_font, button_font) -> None:
        self.screen = screen
        self.font_path = font_path
        self.title_font = title_font
        self.button_font = button_font
        self.screen_manager = screen_manager
        self.arrow_right = pygame.image.load(f'{os.getcwd()}/assets/right_arrow_transparent.png').convert_alpha()
        self.arrow_right = pygame.transform.scale(self.arrow_right, (50, 50))
        self.arrow_right = crop_image(self.arrow_right)
        self.arrow_left = pygame.image.load(f'{os.getcwd()}/assets/left_arrow_transparent.png').convert_alpha()
        self.arrow_left = pygame.transform.scale(self.arrow_left, (50, 50))
        self.arrow_left = crop_image(self.arrow_left)
        self.page_num = 1
        self.current_page = "Basic achievements"

    def achievements_screen(self, title):

        running = True
        while running:
            self.screen.blit(bg, (0,0))

            achievements_title = title
            title_x = WIDTH // 2 - self.title_font.size(achievements_title)[0] // 2
            title_y = HEIGHT // 20
            draw_text_with_outline(self.screen, achievements_title, self.title_font, title_x, title_y)
            back = None
            left_arrow = None

            if self.current_page == "Basic achievements":
                back_button_width = 100
                back_button_height = 70
                back = draw_button(self.screen, "Back", self.button_font, 10, 10, back_button_width, back_button_height, (0, 0, 0), (200, 200, 200))

            elif self.current_page != "Basic achievements":
                left_arrow = draw_button(self.screen, self.arrow_left, self.button_font, 10, 440, 50, 50, (100, 100, 100), (200, 200, 200))

            draw_rect(self.screen, title_x - 25, title_y + 50, 300, 400, (0, 0, 0), 5, 4)
            draw_rect(self.screen, title_x - 20, title_y + 55, 290, 390, (145, 165, 16), 0, 0)
            right_arrow = draw_button(self.screen, self.arrow_right, self.button_font, 420, 440, 50, 50, (100, 100, 100), (200, 200, 200))
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if back:
                    self.screen_manager.main_menu()
                if right_arrow:
                    self.page_num += 1
                    self.determine_page_title()
                    self.achievements_screen(self.current_page)
                if left_arrow:
                    self.page_num -= 1
                    self.determine_page_title()
                    self.achievements_screen(self.current_page)

    def determine_page_title(self):
        page_dict = {1: "Basic achievements", 2: "Milestone achievements", 3: "Skill-based achievements"}

        for key, value in page_dict.items():
            if key == self.page_num:
                self.current_page = value
