import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

#music matters
pygame.mixer.init()


# Initialize joystick subsystem
pygame.joystick.init()
joystick_connected = False
joystick = None
prev_joystick_buttons = []
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joystick_connected = True
    # store previous button states to detect edges (pressed this frame but not previous)
    prev_joystick_buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

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

# Dead zone for analog sticks
JOYSTICK_DEADZONE = 0.3

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
            shoot_sound.play()

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
    # dim the background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(160)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0,0))

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

    #music loop
    pygame.mixer.music.load('assets/sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(-1)  


    #shoot sound
    shoot_sound = pygame.mixer.Sound('assets/sounds/shoot.wav')
    shoot_sound.set_volume(0.7)  

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
        pause_rect = pygame.Rect(WIDTH - 80, 12, 64, 64)  

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

        # draw tanks (only if created)
        if player_tank:
            player_tank.draw()
        if enemy_tank:
            enemy_tank.draw()

        # Draw pause button
        screen.blit(pause_icon, (WIDTH - 80, 12))

        # INPUT HANDLING (combined keyboard + controller)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # Keyboard movement
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1

        # Controller movement (if connected)
        if joystick_connected and joystick:
            try:
                axis_x = joystick.get_axis(0)  # left stick X
                axis_y = joystick.get_axis(1)  # left stick Y
            except Exception:
                axis_x = 0
                axis_y = 0

            # apply deadzone
            if abs(axis_x) > JOYSTICK_DEADZONE:
                dx += axis_x  # axis_x: left = -1, right = +1
            if abs(axis_y) > JOYSTICK_DEADZONE:
                dy += axis_y  # axis_y: up = -1, down = +1 (typically)

            # note: axis_y positive is down; keyboard used dy = -1 for up, so combine works
        # normalize and move & rotate if there's input
        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

            # keyboard uses dy -1 for up; joystick axis_y uses -1 up typically, so direction aligns
            if player_tank:
                player_tank.x += player_tank.speed * dx
                player_tank.y += player_tank.speed * dy
                player_tank.angle = (-math.degrees(math.atan2(-dy, dx))) % 360

        # Keep player inside
        if player_tank:
            player_tank.x = max(25, min(WIDTH - 25, player_tank.x))
            player_tank.y = max(25, min(HEIGHT - 25, player_tank.y))

        # Shooting: continuous when holding space (keyboard) or A (controller button 0)
        shoot_pressed = False
        if keys[pygame.K_SPACE]:
            shoot_pressed = True
        if joystick_connected and joystick:
            # Button 0 is commonly "A" / "Cross"
            if joystick.get_numbuttons() > 0 and joystick.get_button(0):
                shoot_pressed = True

        if shoot_pressed and player_tank:
            player_tank.shoot()

        # Controller Start button handling (edge detect) to toggle pause
        if joystick_connected and joystick:
            num_buttons = joystick.get_numbuttons()
            # check if there is a start button index 7 commonly; otherwise try to be safe
            start_idx = 7 if num_buttons > 7 else (num_buttons - 1)
            cur_buttons = [joystick.get_button(i) for i in range(num_buttons)]
            # detect rising edge for start button if available
            if start_idx >= 0 and start_idx < num_buttons:
                if cur_buttons[start_idx] == 1 and (start_idx >= len(prev_joystick_buttons) or prev_joystick_buttons[start_idx] == 0):
                    # toggle pause
                    if game_state == PLAYING:
                        game_state = PAUSED
                    elif game_state == PAUSED:
                        game_state = PLAYING
            # update prev_joystick_buttons for next frame
            prev_joystick_buttons = cur_buttons

        # ---------------------------
        # Enemy AI 

        if player_tank and enemy_tank:
            ex_dx = player_tank.x - enemy_tank.x
            ex_dy = player_tank.y - enemy_tank.y
            distance = math.hypot(ex_dx, ex_dy)

            # Calculate target angle (toward player's current position)
            target_angle = -math.degrees(math.atan2(-ex_dy, ex_dx)) % 360
            angle_diff = (target_angle - enemy_tank.angle + 360) % 360
            if angle_diff > 180:
                angle_diff -= 180  # NOTE: deliberate small normalize fix below

            # Note: previous versions used normalization to [-180,180].
            angle_diff = (target_angle - enemy_tank.angle + 540) % 360 - 180

            # Determine rotation speed and prioritize turning if behind
            if abs(angle_diff) > 120:
                rot_speed = 12
            elif abs(angle_diff) > 60:
                rot_speed = 8
            else:
                rot_speed = 4

            # Rotate toward player quickly if needed
            if angle_diff > rot_speed:
                enemy_tank.angle += rot_speed
            elif angle_diff < -rot_speed:
                enemy_tank.angle -= rot_speed
            else:
                enemy_tank.angle = target_angle % 360

            enemy_tank.angle %= 360

            # If player is behind (big angle_diff), prioritize rotation (no movement)
            if abs(angle_diff) > 90:
                pass
            else:
                # Movement strategy
                if distance > 250:
                    # Move toward the player
                    enemy_tank.x += enemy_tank.speed * math.cos(math.radians(enemy_tank.angle))
                    enemy_tank.y -= enemy_tank.speed * math.sin(math.radians(enemy_tank.angle))

                elif 120 < distance <= 250:
                    # Strafe (circle) around the player
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

        
        if player_tank and enemy_tank:
            player_tank.update_bullets(enemy_tank)
            enemy_tank.update_bullets(player_tank)

        if player_tank and player_tank.health <= 0:
            winner = "Computer"
            game_state = GAME_OVER
        elif enemy_tank and enemy_tank.health <= 0:
            winner = "Player"
            game_state = GAME_OVER

        pygame.display.flip()

    elif game_state == PAUSED:
        draw_pause_menu(mouse_pos)

    elif game_state == GAME_OVER:
        draw_game_over(mouse_pos)

    # Event handling (mouse + keyboard + joystick edge handled above)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse clicks for menus
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

        # Keyboard shortcuts
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
                # Keyboard pause (Escape)
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSED if game_state == PLAYING else PLAYING
                # Keyboard shoot
                if event.key == pygame.K_SPACE and player_tank:
                    player_tank.shoot()

            elif game_state == PAUSED:
                if event.key == pygame.K_1:
                    game_state = MAP_SELECT
                elif event.key == pygame.K_2:
                    game_state = MENU

            elif game_state == GAME_OVER:
                if event.key == pygame.K_1:
                    game_state = MAP_SELECT
                elif event.key == pygame.K_2:
                    game_state = MENU

    clock.tick(FPS)

pygame.quit()
sys.exit()
