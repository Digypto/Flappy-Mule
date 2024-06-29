import pygame
from pygame.locals import *
import random
import os

# Initialize pygame
pygame.init()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 480
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Mule")
clock = pygame.time.Clock()

bg = pygame.image.load(f'{os.getcwd()}/background.png').convert_alpha()

font = pygame.font.Font(None, 200)
text = font.render('FOOO', True, (255, 0, 0))
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(f'{os.getcwd()}/mule.png')
            self.image = pygame.transform.scale(self.image, (80, 80)) #Resizing
            self.image.convert_alpha()
            self.image = crop_image(self.image)
        except pygame.error as e:
            print(f"Unable to load image: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill(RED)
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
        self.image = pygame.Surface([80, height])
        self.image.fill(GREEN)
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
        self.font = pygame.font.Font(None, 48)  
        self.color = (255, 255, 255) #White rgb
    
    def update_score(self):
        self.points += 1

    def render_score(self):
        score_surface = self.font.render(str(self.points), True, self.color)
        screen.blit(score_surface, (WIDTH // 2, HEIGHT // 7))  #Position


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

def run_game():
    global all_sprites, pipes, last_pipe_time

    all_sprites.empty()  # Clear the sprite groups
    pipes.empty()

    bird = Bird()
    score = Score()
    all_sprites.add(bird)

    running = True
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
            running = False

        all_sprites.draw(screen)
        score.render_score()
        pygame.display.flip()
        clock.tick(60)

    # 4-second delay after dying
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.time.wait(4000) # 4-second delay after dying
    return True

print("Starting the game...")

keep_running = True
while keep_running:
    keep_running = run_game()

pygame.quit()
exit()
