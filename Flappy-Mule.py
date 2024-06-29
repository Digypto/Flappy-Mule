import pygame
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)

WIDTH = 480
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

bg = pygame.image.load("/Users/emil/Desktop/Flappy Bird/background.png").convert_alpha()

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("/Users/emil/Desktop/Flappy Bird/bird.png").convert()
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

def run_game():
    global all_sprites, pipes, last_pipe_time

    all_sprites.empty()  # Clear the sprite groups
    pipes.empty()

    bird = Bird()
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

        pipe_collision = pygame.sprite.spritecollide(bird, pipes, False)
        if pipe_collision:
            running = False

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    # 4-second delay after dying
    pygame.time.wait(4000)
    return True

print("Starting the game...")

keep_running = True
while keep_running:
    keep_running = run_game()

pygame.quit()
exit()
