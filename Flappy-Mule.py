import pygame
from pygame.locals import *
import random
import os

# Initialize pygame
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

bg = pygame.image.load(f'{os.getcwd()}/background.png').convert_alpha()

# Load custom font from Google Fonts
font_path = os.path.join(os.getcwd(), 'BebasNeue-Regular.ttf')
font = pygame.font.Font(font_path, 160)
button_font = pygame.font.Font(font_path, 48)  # Smaller font for the button
score_font = pygame.font.Font(font_path, 120)  # Font for the score

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/mule.png')
        self.image = pygame.transform.scale(self.image, (80, 80)) #Resizing
        self.image.convert_alpha()
        self.image = crop_image(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT // 2
        self.change_y = 0

    def update(self):
        self.change_y += 1
        self.rect.y += self.change_y
        if self.rect.y >= HEIGHT - 50:
            self.rect.y = HEIGHT - 50
            self.change_y = 0
        if self.rect.y <= 0:
            self.rect.y = 0
            self.change_y = 0

    def jump(self):
        self.change_y = -10

class Pipe(pygame.sprite.Sprite):
    def __init__(self, position, height):
        super().__init__()
        self.image = pygame.image.load(f'{os.getcwd()}/pipe.png')
        self.rect = self.image.get_rect()
        if position == "top":
            self.rect.bottom = height
        else:
            self.rect.top = HEIGHT - height
        self.rect.x = WIDTH

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.points = -1
        self.font = pygame.font.Font('BebasNeue-Regular.ttf', 48)  
        self.color = (255, 255, 255) #White rgb
        self.outline_color = BLACK
    
    def update_score(self):
        self.points += 1

    def render_score(self, x, y):
        score_text = str(self.points)
        draw_text_with_outline(score_text, self.font, self.color, self.outline_color, WIDTH // 2, HEIGHT // 7)


# Global sprite groups
all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
last_pipe_time = 0
PIPE_INTERVAL = 1500

def create_pipe():
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

def crop_image(image):
    rect = image.get_bounding_rect()
    cropped_image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cropped_image.blit(image, (0, 0), rect) #Identifies the tranparent parts and removes them
    return cropped_image

def play_collision_sound():
    mule_sound = f'{os.getcwd()}/mule.mp3'
    pygame.mixer.init()
    pygame.mixer.music.load(mule_sound)
    pygame.mixer.music.play()

def draw_text_with_outline(text, font, text_color, outline_color, x, y):
    # Render the text with the outline color multiple times
    outline_positions = [(x-2, y-2), (x+2, y-2), (x-2, y+2), (x+2, y+2), (x-2, y), (x+2, y), (x, y-2), (x, y+2)]
    for pos in outline_positions:
        outline_text = font.render(text, True, BLACK)
        screen.blit(outline_text, pos)

    # Render the text with the main color
    main_text = font.render(text, True, WHITE)
    screen.blit(main_text, (x, y))

def draw_button(text, font, x, y, width, height, inactive_color, active_color):
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

def game_over_screen(score):
    game_over_text = "FOOO"
    text_x = WIDTH // 2 - font.size(game_over_text)[0] // 2
    text_y = HEIGHT // 2 - font.size(game_over_text)[1] // 2 - 150
    draw_text_with_outline(game_over_text, font, WHITE, BLACK, text_x, text_y)

    # Render the score below the "FOOO" text
    score_label = "Score: " + str(score.points)
    score_x = WIDTH // 3 - font.size(str(score.points))[1] // 2
    score_y = text_y + font.size(game_over_text)[1] + 20  # Position below "FOOO" text
    draw_text_with_outline(score_label, score_font, WHITE, BLACK, score_x, score_y)

    # Draw "Play Again" button
    button_x = WIDTH // 2 - 100
    button_y = score_y + font.size(str(score.points))[1] - 10
    button_width = 200
    button_height = 70

    while True:
        play_again = draw_button("Play Again", button_font, button_x, button_y, button_width, button_height, BLACK, LIGHT_GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.time.wait(1000)  # Small delay after dying
                    return True
            if play_again:
                return True

def run_game():
    global all_sprites, pipes, last_pipe_time

    all_sprites.empty()  # Clear the sprite groups
    pipes.empty()

    bird = Bird()
    score = Score()
    all_sprites.add(bird)

    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
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
            score.update_score()

        pipe_collision = pygame.sprite.spritecollide(bird, pipes, False)
        if pipe_collision:
            play_collision_sound()
            running = False

        all_sprites.draw(screen)
        if running:
            score.render_score(WIDTH // 2, HEIGHT // 7)
        pygame.display.flip()
        clock.tick(60)

    return game_over_screen(score)

keep_running = True
while keep_running:
    keep_running = run_game()

pygame.quit()
exit()