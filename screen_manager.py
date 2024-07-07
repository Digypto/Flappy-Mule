import pygame
from drawing import draw_text_with_outline, draw_button
from player import Player
from db.db_operations import save_score, get_high_scores
from db.db_connection import get_db_connection, retrieve_db_credentials
import os


from db.db_operations import get_worst_score_in_db
from db.db_connection import get_db_connection, retrieve_db_credentials
from sound_manager import play_coin_collision_sound, play_collision_sound, play_powerup_collision_sound

from player import Player
from game_objects import Mule, PowerUp, all_sprites, pipes, coins, powerups, last_pipe_time, PIPE_INTERVAL, create_coin, create_pipe, create_powerup
from drawing import draw_text_with_outline

credential_dict = retrieve_db_credentials()
user = credential_dict.get("user")
password = credential_dict.get("password")
host = credential_dict.get("host")
appname = credential_dict.get("appname")
client = get_db_connection(user, password, host, appname)

clock = pygame.time.Clock()

WIDTH = 480
HEIGHT = 500

bg = pygame.image.load(f'{os.getcwd()}/assets/background.png').convert_alpha()


class ScreenManager:
    def __init__(self, screen, font_path):
        self.screen = screen
        self.font_path = font_path
        self.load_fonts()

    def load_fonts(self):
        self.base_font = pygame.font.Font(self.font_path, 32)
        self.leaderboard_font = pygame.font.Font(self.font_path, 36)
        self.congratulations_font = pygame.font.Font(self.font_path, 28)
        self.title_font = pygame.font.Font(self.font_path, 90)
        self.game_over_font = pygame.font.Font(self.font_path, 160)
        self.button_font = pygame.font.Font(self.font_path, 48)
        self.score_font = pygame.font.Font(self.font_path, 120)

    def ask_username_screen(self, player: Player):
        score_label = "Score: " + str(player.points)
        score_x = WIDTH // 3 - self.score_font.size(str(player.points))[1] // 2
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
                    self.main_menu()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            player.update_name(user_text)
                            save_score(client, player.points, player.name)
                            user_text = ''
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

    def game_over_screen(self, player: Player):
        game_over_text = "FOOO"
        text_x = WIDTH // 2 - self.game_over_font.size(game_over_text)[0] // 2
        text_y = HEIGHT // 2 - self.game_over_font.size(game_over_text)[1] // 2 - 150
        draw_text_with_outline(self.screen, game_over_text, self.game_over_font, text_x, text_y)

        score_label = "Score: " + str(player.points)
        score_x = WIDTH // 3 - self.score_font.size(str(player.points))[1] // 2
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
            leaderboard = draw_button(self.screen, "Leaderboard", self.button_font, button_x, button_y + 100, button_width + 50, button_height, (0, 0, 0), (200, 200, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if play:
                    self.run_game()
                if leaderboard:
                    self.display_leaderboard()

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
                    pass
                if guest:
                    self.main_menu()

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
        player = Player()
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
            return self.ask_username_screen(player)
        if get_worst_score_in_db(client)[0] >= player.points:
            return self.game_over_screen(player)

