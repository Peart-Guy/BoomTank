import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 770
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Fight")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 255, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("Arial", 40)

# Load assets
tank_red = pygame.transform.scale(pygame.image.load("assets/red_tank.png"), (50, 50))
tank_blue = pygame.transform.scale(pygame.image.load("assets/blue_tank.png"), (50, 50))

# Map backgrounds
desert_map = pygame.transform.scale(pygame.image.load("assets/desert.png"), (WIDTH, HEIGHT))
forest_map = pygame.transform.scale(pygame.image.load("assets/forest.png"), (WIDTH, HEIGHT))

bullet_img = pygame.Surface((10, 4))
bullet_img.fill(BLACK)

# Game states
MENU = "menu"
TANK_SELECT = "tank_select"
MAP_SELECT = "map_select"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU
player_color = None
winner = None
selected_map = None  # NEW

# Tank Class
class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3
        self.color = color
        self.image = tank_red if color == "red" else tank_blue
        self.health = 100
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_delay = 200  # milliseconds

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, rect.topleft)

        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - 25, self.y - 40, 50, 8))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y - 40, 50 * (self.health / 100), 8))

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_delay:
            dx = math.cos(math.radians(self.angle))   # X direction
            dy = math.sin(math.radians(self.angle))   # Y direction

            # Offset from the tank center to the barrel tip
            barrel_length = 30
            offset_x = dx * barrel_length
            offset_y = dy * barrel_length

            self.bullets.append([self.x + offset_x, self.y + offset_y, dx, dy])
            self.last_shot_time = current_time

    def update_bullets(self, opponent):
        for bullet in self.bullets[:]:
            bullet[0] += bullet[2] * 10
            bullet[1] += bullet[3] * 10
            if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
                self.bullets.remove(bullet)
            elif math.hypot(bullet[0] - opponent.x, bullet[1] - opponent.y) < 25:
                opponent.health -= 10
                self.bullets.remove(bullet)

        for bullet in self.bullets:
            pygame.draw.rect(screen, BLACK, (bullet[0], bullet[1], 6, 3))

# UI Screens
def draw_menu():
    screen.fill(WHITE)
    title = font.render("Tank Fight", True, BLACK)
    start = font.render("1. Start Game", True, BLACK)
    quit_game = font.render("2. Quit", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(start, (WIDTH//2 - start.get_width()//2, 250))
    screen.blit(quit_game, (WIDTH//2 - quit_game.get_width()//2, 320))
    pygame.display.flip()

def draw_tank_select():
    screen.fill(WHITE)
    text = font.render("Choose Tank: 1. Red  2. Blue", True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    pygame.display.flip()

def draw_map_select():
    screen.fill(WHITE)
    text = font.render("Choose Map:", True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 100))

    desert_text = font.render("1. Desert", True, BLACK)
    forest_text = font.render("2. Forest", True, BLACK)
    screen.blit(desert_text, (WIDTH//2 - desert_text.get_width()//2, 250))
    screen.blit(forest_text, (WIDTH//2 - forest_text.get_width()//2, 320))
    pygame.display.flip()

def draw_game_over():
    screen.fill(WHITE)
    text = font.render(f"{winner} Won!", True, BLACK)
    replay = font.render("1. Replay", True, BLACK)
    menu = font.render("2. Main Menu", True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
    screen.blit(replay, (WIDTH//2 - replay.get_width()//2, 300))
    screen.blit(menu, (WIDTH//2 - menu.get_width()//2, 360))
    pygame.display.flip()

# Game variables
player_tank = None
enemy_tank = None

# Main loop
running = True
while running:
    if game_state == MENU:
        draw_menu()

    elif game_state == TANK_SELECT:
        draw_tank_select()

    elif game_state == MAP_SELECT:
        draw_map_select()

    elif game_state == PLAYING:
        # Draw selected map
        if selected_map == "desert":
            screen.blit(desert_map, (0, 0))
        elif selected_map == "forest":
            screen.blit(forest_map, (0, 0))

        # Draw tanks
        player_tank.draw()
        enemy_tank.draw()

        # Controls
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

            player_tank.x += player_tank.speed * dx
            player_tank.y += player_tank.speed * dy
            player_tank.angle = (-math.degrees(math.atan2(-dy, dx))) % 360

        # Boundary check
        player_tank.x = max(25, min(WIDTH - 25, player_tank.x))
        player_tank.y = max(25, min(HEIGHT - 25, player_tank.y))

        # Enemy AI
        dx = player_tank.x - enemy_tank.x
        dy = player_tank.y - enemy_tank.y
        distance = math.hypot(dx, dy)

        target_angle = math.degrees(math.atan2(-dy, dx))
        angle_diff = (target_angle - enemy_tank.angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360

        if angle_diff > 2:
            enemy_tank.angle += 2
        elif angle_diff < -2:
            enemy_tank.angle -= 2

        if distance > 200:
            enemy_tank.x += enemy_tank.speed * math.cos(math.radians(enemy_tank.angle))
            enemy_tank.y -= enemy_tank.speed * math.sin(math.radians(enemy_tank.angle))

        if abs(angle_diff) < 10 and random.randint(0, 15) == 0:
            enemy_tank.shoot()

        # Update bullets
        player_tank.update_bullets(enemy_tank)
        enemy_tank.update_bullets(player_tank)

        if player_tank.health <= 0:
            winner = "Computer"
            game_state = GAME_OVER
        elif enemy_tank.health <= 0:
            winner = "Player"
            game_state = GAME_OVER

        pygame.display.flip()

    elif game_state == GAME_OVER:
        draw_game_over()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_1:
                    game_state = TANK_SELECT
                elif event.key == pygame.K_2:
                    running = False
            elif game_state == TANK_SELECT:
                if event.key == pygame.K_1:
                    player_color = "red"
                    game_state = MAP_SELECT
                elif event.key == pygame.K_2:
                    player_color = "blue"
                    game_state = MAP_SELECT
            elif game_state == MAP_SELECT:
                if event.key == pygame.K_1:
                    selected_map = "desert"
                    player_tank = Tank(100, HEIGHT//2, player_color)
                    enemy_color = "blue" if player_color == "red" else "red"
                    enemy_tank = Tank(WIDTH - 100, HEIGHT//2, enemy_color)
                    game_state = PLAYING
                elif event.key == pygame.K_2:
                    selected_map = "forest"
                    player_tank = Tank(100, HEIGHT//2, player_color)
                    enemy_color = "blue" if player_color == "red" else "red"
                    enemy_tank = Tank(WIDTH - 100, HEIGHT//2, enemy_color)
                    game_state = PLAYING
            elif game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    player_tank.shoot()
            elif game_state == GAME_OVER:
                if event.key == pygame.K_1:
                    game_state = MAP_SELECT
                elif event.key == pygame.K_2:
                    game_state = MENU

    clock.tick(FPS)

pygame.quit()
sys.exit()
