import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 770
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOOMTANK")

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

desert_map = pygame.transform.scale(pygame.image.load("assets/desert.png"), (WIDTH, HEIGHT))
forest_map = pygame.transform.scale(pygame.image.load("assets/forest.png"), (WIDTH, HEIGHT))

bullet_img = pygame.Surface((10, 4))
bullet_img.fill(BLACK)

# Menu Backgrounds
menu_bg = pygame.transform.scale(pygame.image.load("assets/menu_bg.png"), (WIDTH, HEIGHT))
tank_select_bg = pygame.transform.scale(pygame.image.load("assets/menu_bg.png"), (WIDTH, HEIGHT))
map_select_bg = pygame.transform.scale(pygame.image.load("assets/menu_bg.png"), (WIDTH, HEIGHT))
game_over_bg = pygame.transform.scale(pygame.image.load("assets/menu_bg.png"), (WIDTH, HEIGHT))

# Map thumbnails
desert_thumb = pygame.transform.scale(pygame.image.load("assets/desert.png"), (150, 100))
forest_thumb = pygame.transform.scale(pygame.image.load("assets/forest.png"), (150, 100))

# Pause icon
pause_icon = pygame.transform.scale(pygame.image.load("assets/pause.png"), (80, 80))

# Game states
MENU = "menu"
TANK_SELECT = "tank_select"
MAP_SELECT = "map_select"
PLAYING = "playing"
GAME_OVER = "game_over"
PAUSED = "paused"

game_state = MENU
player_color = None
winner = None
selected_map = None

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
        self.shoot_delay = 200 

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
            dx = math.cos(math.radians(self.angle))
            dy = math.sin(math.radians(self.angle))
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
def draw_menu(mouse_pos):
    screen.blit(menu_bg, (0, 0))
    title = font.render("Tank Fight", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    start_color = (100, 100, 255) if start_rect.collidepoint(mouse_pos) else (0, 0, 180)
    quit_color = (255, 100, 100) if quit_rect.collidepoint(mouse_pos) else (180, 0, 0)

    pygame.draw.rect(screen, start_color, start_rect, border_radius=15)
    pygame.draw.rect(screen, quit_color, quit_rect, border_radius=15)

    start_text = font.render("Start Game", True, WHITE)
    quit_text = font.render("Quit", True, WHITE)
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 265))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, 355))
    pygame.display.flip()

def draw_tank_select(mouse_pos):
    screen.blit(tank_select_bg, (0, 0))
    text = font.render("Choose Your Tank", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))

    if red_rect.collidepoint(mouse_pos):
        img = pygame.transform.scale(tank_red, (120, 120))
    else:
        img = pygame.transform.scale(tank_red, (100, 100))
    screen.blit(img, red_rect.topleft)

    if blue_rect.collidepoint(mouse_pos):
        img = pygame.transform.scale(tank_blue, (120, 120))
    else:
        img = pygame.transform.scale(tank_blue, (100, 100))
    screen.blit(img, blue_rect.topleft)

    pygame.display.flip()

def draw_map_select(mouse_pos):
    screen.blit(map_select_bg, (0, 0))
    text = font.render("Choose Map", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))

    screen.blit(desert_thumb, desert_rect.topleft)
    screen.blit(forest_thumb, forest_rect.topleft)

    pygame.display.flip()

def draw_game_over(mouse_pos):
    screen.blit(game_over_bg, (0, 0))
    text = font.render(f"{winner} Won!", True, WHITE)
    replay = font.render("Replay", True, WHITE)
    menu = font.render("Main Menu", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
    screen.blit(replay, (WIDTH//2 - replay.get_width()//2, 300))
    screen.blit(menu, (WIDTH//2 - menu.get_width()//2, 360))
    pygame.display.flip()

def draw_pause_menu(mouse_pos):
    pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))  
    text = font.render("PAUSED", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))

    resume_color = (100, 200, 100) if resume_rect.collidepoint(mouse_pos) else (0, 150, 0)
    exit_color = (200, 100, 100) if exit_rect.collidepoint(mouse_pos) else (150, 0, 0)

    pygame.draw.rect(screen, resume_color, resume_rect, border_radius=15)
    pygame.draw.rect(screen, exit_color, exit_rect, border_radius=15)

    resume_text = font.render("Resume", True, WHITE)
    exit_text = font.render("Main Menu", True, WHITE)

    screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, 315))
    screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, 395))
    pygame.display.flip()

# Game variables
player_tank = None
enemy_tank = None

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    # Define rects for current state
    if game_state == MENU:
        start_rect = pygame.Rect(WIDTH//2 - 150, 250, 300, 60)
        quit_rect = pygame.Rect(WIDTH//2 - 150, 340, 300, 60)

    elif game_state == TANK_SELECT:
        red_rect = pygame.Rect(WIDTH//2 - 200, 200, 100, 100)
        blue_rect = pygame.Rect(WIDTH//2 + 100, 200, 100, 100)

    elif game_state == MAP_SELECT:
        desert_rect = pygame.Rect(WIDTH//2 - 250, 250, 150, 100)
        forest_rect = pygame.Rect(WIDTH//2 + 100, 250, 150, 100)

    elif game_state == PLAYING:
        pause_rect = pygame.Rect(WIDTH - 60, 20, 40, 40)

    elif game_state == GAME_OVER:
        replay_rect = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
        menu_rect = pygame.Rect(WIDTH//2 - 150, 360, 300, 60)

    elif game_state == PAUSED:
        resume_rect = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
        exit_rect = pygame.Rect(WIDTH//2 - 150, 380, 300, 60)

    # Draw UI
    if game_state == MENU:
        draw_menu(mouse_pos)
    elif game_state == TANK_SELECT:
        draw_tank_select(mouse_pos)
    elif game_state == MAP_SELECT:
        draw_map_select(mouse_pos)
    elif game_state == PLAYING:
        if selected_map == "desert":
            screen.blit(desert_map, (0, 0))
        elif selected_map == "forest":
            screen.blit(forest_map, (0, 0))

        player_tank.draw()
        enemy_tank.draw()

        # Draw pause button
        screen.blit(pause_icon, (WIDTH - 60, 20))

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

        player_tank.x = max(25, min(WIDTH - 25, player_tank.x))
        player_tank.y = max(25, min(HEIGHT - 25, player_tank.y))

        # ---------------------------
        # Enemy AI 
 
        dx = player_tank.x - enemy_tank.x
        dy = player_tank.y - enemy_tank.y
        distance = math.hypot(dx, dy)

        # Calculate target angle
        target_angle = -math.degrees(math.atan2(-dy, dx)) % 360
        angle_diff = (target_angle - enemy_tank.angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360  # Normalize to [-180, 180]

        # Determine rotation speed
        if abs(angle_diff) > 120:
            rot_speed = 12  # Very fast if player is behind
        elif abs(angle_diff) > 60:
            rot_speed = 8
        else:
            rot_speed = 4

        # Rotate towards player
        if angle_diff > rot_speed:
            enemy_tank.angle += rot_speed
        elif angle_diff < -rot_speed:
            enemy_tank.angle -= rot_speed
        else:
            enemy_tank.angle = target_angle % 360

        enemy_tank.angle %= 360

        # If player is behind (angle_diff > 90), STOP moving and rotate first
        if abs(angle_diff) > 90:
            # Just rotate this frame, no movement
            pass
        else:
            # Movement strategy
            if distance > 250:
                # Move toward the player
                enemy_tank.x += enemy_tank.speed * math.cos(math.radians(enemy_tank.angle))
                enemy_tank.y -= enemy_tank.speed * math.sin(math.radians(enemy_tank.angle))

            elif 120 < distance <= 250:
                # Strafe  around the player
                if ((pygame.time.get_ticks() // 500) % 2) == 0:
                    strafe_angle = enemy_tank.angle + 90
                else:
                    strafe_angle = enemy_tank.angle - 90
                enemy_tank.x += enemy_tank.speed * 0.9 * math.cos(math.radians(strafe_angle))
                enemy_tank.y -= enemy_tank.speed * 0.9 * math.sin(math.radians(strafe_angle))

            else:
                # Too close — back away
                enemy_tank.x -= enemy_tank.speed * 0.8 * math.cos(math.radians(enemy_tank.angle))
                enemy_tank.y += enemy_tank.speed * 0.8 * math.sin(math.radians(enemy_tank.angle))

        # Keep enemy inside the map
        enemy_tank.x = max(25, min(WIDTH - 25, enemy_tank.x))
        enemy_tank.y = max(25, min(HEIGHT - 25, enemy_tank.y))

        # Shooting logic 
        if abs(angle_diff) < 6:
            if distance < 140:
                enemy_tank.shoot()
            else:
                chance = 6 if distance > 250 else 3
                if random.randint(0, chance) == 0:
                    enemy_tank.shoot()



        player_tank.update_bullets(enemy_tank)
        enemy_tank.update_bullets(player_tank)

        if player_tank.health <= 0:
            winner = "Computer"
            game_state = GAME_OVER
        elif enemy_tank.health <= 0:
            winner = "Player"
            game_state = GAME_OVER

        pygame.display.flip()

    elif game_state == PAUSED:
        draw_pause_menu(mouse_pos)

    elif game_state == GAME_OVER:
        draw_game_over(mouse_pos)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            if game_state == MENU:
                if start_rect.collidepoint(mouse_pos):
                    game_state = TANK_SELECT
                elif quit_rect.collidepoint(mouse_pos):
                    running = False

            elif game_state == TANK_SELECT:
                if red_rect.collidepoint(mouse_pos):
                    player_color = "red"
                    game_state = MAP_SELECT
                elif blue_rect.collidepoint(mouse_pos):
                    player_color = "blue"
                    game_state = MAP_SELECT

            elif game_state == MAP_SELECT:
                if desert_rect.collidepoint(mouse_pos):
                    selected_map = "desert"
                    player_tank = Tank(100, HEIGHT//2, player_color)
                    enemy_color = "blue" if player_color == "red" else "red"
                    enemy_tank = Tank(WIDTH - 100, HEIGHT//2, enemy_color)
                    game_state = PLAYING
                elif forest_rect.collidepoint(mouse_pos):
                    selected_map = "forest"
                    player_tank = Tank(100, HEIGHT//2, player_color)
                    enemy_color = "blue" if player_color == "red" else "red"
                    enemy_tank = Tank(WIDTH - 100, HEIGHT//2, enemy_color)
                    game_state = PLAYING

            elif game_state == PLAYING:
                if pause_rect.collidepoint(mouse_pos):
                    game_state = PAUSED

            elif game_state == PAUSED:
                if resume_rect.collidepoint(mouse_pos):
                    game_state = PLAYING
                elif exit_rect.collidepoint(mouse_pos):
                    game_state = MENU

            elif game_state == GAME_OVER:
                if replay_rect.collidepoint(mouse_pos):
                    game_state = MAP_SELECT
                elif menu_rect.collidepoint(mouse_pos):
                    game_state = MENU

        if event.type == pygame.KEYDOWN:
            if game_state == PLAYING and event.key == pygame.K_SPACE:
                player_tank.shoot()

    clock.tick(FPS)

pygame.quit()
sys.exit()
