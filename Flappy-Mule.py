import pygame
from pygame.locals import *
import random
import os
import ctypes
from db.db_operations import save_score, get_high_scores, get_worst_score_in_db
from db.db_connection import get_db_connection, retrieve_db_credentials


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

class Mule(pygame.sprite.Sprite):
    """
    Represents the mule that the player controls.

    Attributes
    ----------
    image : pygame.Surface
        The image of the mule.
    rect : pygame.Rect
        The rectangle representing the mule's position and size.
    change_y : int
        The change in the mule's y-coordinate (vertical velocity).
    """
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/assets/mule.png')
        self.image = pygame.transform.scale(self.image, (80, 80))  # Resizing
        self.image.convert_alpha()
        self.image = crop_image(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT // 2
        self.change_y = 0

    def update(self) -> None:
        """
        Updates the mule's position and handles vertical movement.
        """
        self.change_y += 1
        self.rect.y += self.change_y
        if self.rect.y >= HEIGHT - 50:
            self.rect.y = HEIGHT - 50
            self.change_y = 0
        if self.rect.y <= 0:
            self.rect.y = 0
            self.change_y = 0

    def jump(self) -> None:
        """
        Makes the mule jump by setting its vertical velocity.
        """
        self.change_y = -10

class Pipe(pygame.sprite.Sprite):
    """
    Represents a pipe obstacle in the game.

    Attributes
    ----------
    image : pygame.Surface
        The image of the pipe.
    rect : pygame.Rect
        The rectangle representing the pipe's position and size.
    """
    def __init__(self, position: str, height: int) -> None:
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/assets/fence.png')
        self.rect = self.image.get_rect()
        if position == "top":
            self.rect.bottom = height
        else:
            self.rect.top = HEIGHT - height
        self.rect.x = WIDTH

    def update(self) -> None:
        """
        Updates the pipe's position and removes it if it goes off-screen.
        """
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    """
    Represents the user in the game.

    Attributes
    ----------
    points : int
        The current score.
    name : str
        The name of the user (if asked)
    font : pygame.font.Font
        The font used to render the score.
    color : tuple[int, int, int]
        The color of the score text.
    outline_color : tuple[int, int, int]
        The color of the score text outline.
    """
    def __init__(self) -> None:
        super().__init__()
        self.points = -1
        self.name = ""
        self.font = pygame.font.Font('assets/BebasNeue-Regular.ttf', 48)
        self.color = (255, 255, 255)  # White rgb
        self.outline_color = BLACK

    def update_score(self) -> None:
        """
        Increases the score by 1 point.
        """
        self.points += 1

    def update_name(self, name) -> None:
        """
        Adds a name to the user.
        """
        self.name = name

    def render_score(self, x: int, y: int) -> None:
        """
        Renders the score on the screen.

        Parameters
        ----------
        x : int
            The x-coordinate where the score will be rendered.
        y : int
            The y-coordinate where the score will be rendered.
        """
        score_text = str(self.points)
        draw_text_with_outline(score_text, self.font, self.color, self.outline_color, WIDTH // 2, HEIGHT // 7)

# Global sprite groups
all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
last_pipe_time = 0
PIPE_INTERVAL = 1500

def create_pipe() -> None:
    """
    Creates a pair of top and bottom pipes with a gap between them,
    and adds them to the sprite groups.
    """
    global all_sprites, pipes, last_pipe_time

    # Define the gap size between top and bottom pipes (adjust if the game is too easy or hard)
    gap_size = 200

    # Randomly determine the position of the gap
    min_gap_position = 100
    max_gap_position = HEIGHT - 100 - gap_size
    gap_position = random.randint(min_gap_position, max_gap_position)

    top_pipe = Pipe("top", gap_position)
    bottom_pipe = Pipe("bottom", HEIGHT - gap_position - gap_size)

    # Add the pipes to the sprite groups
    all_sprites.add(top_pipe, bottom_pipe)
    pipes.add(top_pipe, bottom_pipe)

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

def draw_text_with_outline(text: str, font: pygame.font.Font, text_color: tuple[int, int, int], outline_color: tuple[int, int, int], x: int, y: int) -> None:
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

def draw_button(text: str, font: pygame.font.Font, x: int, y: int, width: int, height: int, inactive_color: tuple[int, int, int], active_color: tuple[int, int, int]) -> bool:
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


def ask_username_screen(player: Player):

    save_score(client, player.points, player.name)  # Save the score to the database

    score_label = "Score: " + str(player.points)
    score_x = WIDTH // 3 - font.size(str(player.points))[1] // 2
    #score_y = text_y + 175 # Position below "FOOO" text
    score_y = HEIGHT // 2 - font.size(score_label)[1] // 2 - 150
    draw_text_with_outline(score_label, score_font, WHITE, BLACK, score_x, score_y)

    congratulations_text = "Wow, you are in the top 5 of the biggest mules!"
    text_x = 25
    text_y = score_y + 175
    draw_text_with_outline(congratulations_text, leaderboard_font, WHITE, BLACK, text_x, text_y)


    username_label = "Enter a username to get on the leaderboard."
    username_x = 25
    username_y = text_y + 40 # Position below the former text
    draw_text_with_outline(username_label, leaderboard_font, WHITE, BLACK, username_x, username_y)


    # Draw "Yes" button
    yes_x = WIDTH // 2 - 125
    yes_y = username_y + 50
    yes_width = 100
    yes_height = 70


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
                        ctypes.windll.user32.MessageBoxW(0, "Score saved!", "Popup", 0)
                        Player().update_name(user_text)
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
            text_surface = base_font.render("The name of the awesome mule", True, (180, 180, 180))  # Lighter color for placeholder
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
    save_score(client, player.points, player.name)  # Save the score to the database
    high_scores = get_high_scores(client)  # Retrieve the top scores

    game_over_text = "FOOO"
    text_x = WIDTH // 2 - font.size(game_over_text)[0] // 2
    text_y = HEIGHT // 2 - font.size(game_over_text)[1] // 2 - 150
    draw_text_with_outline(game_over_text, font, WHITE, BLACK, text_x, text_y)

    # Render the score below the "FOOO" text
    score_label = "Score: " + str(player.points)
    score_x = WIDTH // 3 - font.size(str(player.points))[1] // 2 + 25
    score_y = text_y + 175 # Position below "FOOO" text
    draw_text_with_outline(score_label, score_font, WHITE, BLACK, score_x, score_y)

    death_time = pygame.time.get_ticks() # record the time when the mule dies

    for score_doc in high_scores:
        score_value = score_doc.get('score')  # Accessing the 'score' field from the document


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

    high_scores = get_high_scores(client)

    running = True
    while running:
        screen.blit(bg, (0,0))

        # Draw title
        leaderboard_title = "Leaderboard"
        title_x = WIDTH // 2 - title_font.size(leaderboard_title)[0] // 2
        title_y = HEIGHT // 8
        draw_text_with_outline(leaderboard_title, title_font, WHITE, BLACK, title_x, title_y)

        # Draw scores
        for i, score_doc in enumerate(high_scores):
            score_value = score_doc.get('score')  # Accessing the 'score' field from the document
            score_text = f"{i + 1}. {score_value}"
            text_x = WIDTH // 2 - leaderboard_font.size(score_text)[0] // 2
            text_y = title_y + (i + 1) * 50
            draw_text_with_outline(score_text, leaderboard_font, WHITE, BLACK, text_x, text_y)
        
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
        draw_text_with_outline(flappy_title, title_font, WHITE, BLACK, flappy_x, flappy_y)


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
    global all_sprites, pipes, last_pipe_time

    all_sprites.empty()  # Clear the sprite groups
    pipes.empty()

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
            last_pipe_time = current_time
            player.update_score()

        pipe_collision = pygame.sprite.spritecollide(mule, pipes, False)
        if pipe_collision:
            play_collision_sound()
            running = False

        all_sprites.draw(screen)
        if running and player.points >= 0:
            player.render_score(WIDTH // 2, HEIGHT // 7)
        pygame.display.flip()
        clock.tick(60)

    player.points = get_worst_score_in_db(client)[0] + 1

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


