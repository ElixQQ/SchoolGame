import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 400, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("KlassenKletterer")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

font = pygame.font.Font(None, 36)

bg_image = pygame.image.load("assets/bg.png").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
menu_bg = pygame.image.load("assets/menu_bg.png").convert()
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

player_name = ""
name_entered = False
score = 0
highscore = 0
in_game = False
game_over = False
start_ticks = 0
camera_offset = 0

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
player = None

first_frame = True
initialized = False

def get_hs_filename(name):
    safe = name.replace(" ", "_") if name else "guest"
    return f"{safe}_highscore.txt"

def load_highscore(name):
    filename = get_hs_filename(name)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_highscore(name, new_score):
    filename = get_hs_filename(name)
    with open(filename, "w") as f:
        f.write(str(new_score))

def draw_text_with_outline(surface, text, font, x, y, text_color, outline_color, outline_width=1):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, (x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 50))
        self.rect = self.image.get_rect()
        self.vel_y = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 5
        self.vel_y += 0.4
        self.rect.y += self.vel_y
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w=60, h=10):
        super().__init__()
        self.image = pygame.image.load("assets/pen.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, w=60, h=10, speed=4.5):
        super().__init__(x, y, w, h)
        self.image = pygame.image.load("assets/eraser.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (w, h))
        self.speed = speed
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0:
            self.rect.left = 0
            self.direction = 1
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.direction = -1

def new_platforms_if_needed():
    global score
    highest_y = min(plat.rect.y for plat in platforms)
    while highest_y > 0:
        dy = 100
        last_plat = platforms.sprites()[-1]
        for _ in range(10):
            dx = random.randint(-100, 100)
            new_x = max(0, min(WIDTH - 60, last_plat.rect.x + dx))
            if abs(new_x - last_plat.rect.x) > 20:
                break
        new_y = highest_y - dy
        new_p = MovingPlatform(new_x, new_y) if random.random() < 0.3 else Platform(new_x, new_y)
        all_sprites.add(new_p)
        platforms.add(new_p)
        if initialized:
            score += 1
        highest_y = new_y

def show_name_input():
    screen.blit(menu_bg, (0, 0))
    draw_text_with_outline(screen, "Enter Your Name:", font, WIDTH//2 - 100, HEIGHT//2 - 50, WHITE, BLACK)
    txt_surface = font.render(player_name, True, WHITE)
    input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 36)
    pygame.draw.rect(screen, GREY, input_rect)
    screen.blit(txt_surface, (input_rect.x+5, input_rect.y+5))
    pygame.display.flip()

def show_menu():
    screen.blit(menu_bg, (0, 0))
    draw_text_with_outline(screen, f"Player: {player_name}", font, 10, 10, WHITE, BLACK)
    draw_text_with_outline(screen, "KlassenKletterer", font, WIDTH//2 - 90, HEIGHT//2 - 150, WHITE, BLACK)
    draw_text_with_outline(screen, "Press ENTER to Start", font, WIDTH//2 - 110, HEIGHT//2 - 80, WHITE, BLACK)
    draw_text_with_outline(screen, "Press ESC to Quit", font, WIDTH//2 - 100, HEIGHT//3 + 130, WHITE, BLACK)
    draw_text_with_outline(screen, f"High Score: {highscore}", font, WIDTH//2 - 80, HEIGHT//2 - 250, WHITE, BLACK)
    pygame.display.flip()

def show_game_over():
    screen.blit(menu_bg, (0, 0))
    draw_text_with_outline(screen, "Game Over", font, WIDTH//2 - 50, HEIGHT//2 - 160, WHITE, BLACK)
    draw_text_with_outline(screen, f"Score: {score}", font, WIDTH//2 - 50, HEIGHT//2 - 120, WHITE, BLACK)
    draw_text_with_outline(screen, f"High Score: {highscore}", font, WIDTH//2 - 70, HEIGHT//3 - 100, WHITE, BLACK)
    draw_text_with_outline(screen, "Press SPACE to Restart", font, WIDTH//2 - 120, HEIGHT//2 - 70, WHITE, BLACK)
    pygame.display.flip()

def reset_game():
    global all_sprites, platforms, player, score, in_game, game_over, start_ticks, camera_offset, highscore, initialized
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    start_plat = Platform(WIDTH//2 - 30, HEIGHT - 50)
    all_sprites.add(start_plat)
    platforms.add(start_plat)
    camera_offset = 0
    prev_x, prev_y = start_plat.rect.x, start_plat.rect.y
    for _ in range(6):
        dy = random.randint(60, 100)
        for _ in range(10):
            dx = random.randint(-100, 100)
            new_x = max(0, min(WIDTH - 60, prev_x + dx))
            if abs(new_x - prev_x) > 20:
                break
        new_y = prev_y - dy
        p = MovingPlatform(new_x, new_y) if random.random() < 0.3 else Platform(new_x, new_y)
        all_sprites.add(p)
        platforms.add(p)
        prev_x, prev_y = new_x, new_y
    player = Player()
    player.rect.midbottom = start_plat.rect.midtop
    all_sprites.add(player)
    score = 0
    in_game = True
    game_over = False
    start_ticks = pygame.time.get_ticks()
    highscore = load_highscore(player_name)
    initialized = True

running = True
while running:
    if not name_entered:
        show_name_input()
    elif not in_game and not game_over:
        show_menu()
    elif game_over:
        show_game_over()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not name_entered:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    name_entered = True
                    highscore = load_highscore(player_name)
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not in_game and not game_over:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and game_over:
                    reset_game()

    if in_game:
        clock.tick(60)
        all_sprites.update()

        if score > 8:
            camera_offset += 1
            for plat in platforms:
                plat.rect.y += 1
            player.rect.y += 1

        if not first_frame:
            new_platforms_if_needed()
        else:
            first_frame = False

        if player.vel_y > 0:
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                player.rect.bottom = hits[0].rect.top
                player.vel_y = -10

        if player.rect.top > HEIGHT:
            in_game = False
            game_over = True
            if score > highscore:
                highscore = score
                save_highscore(player_name, highscore)

        if player.rect.top < HEIGHT // 2:
            camera_scroll = HEIGHT // 2 - player.rect.top
            player.rect.top = HEIGHT // 2
            for plat in platforms:
                plat.rect.y += camera_scroll
            score += camera_scroll // 100

        new_platforms_if_needed()

        bg_h = bg_image.get_height()
        y0 = +(camera_offset % bg_h)
        for i in range(-1, HEIGHT // bg_h + 2):
            screen.blit(bg_image, (0, y0 - i * bg_h))

        all_sprites.draw(screen)

        draw_text_with_outline(screen, f"Score: {score}", font, 10, 10, WHITE, BLACK)
        draw_text_with_outline(screen, f"High Score: {highscore}", font, 10, 40, WHITE, BLACK)
        elapsed = (pygame.time.get_ticks() - start_ticks) // 1000
        mins, secs = divmod(elapsed, 60)
        timer = f"{mins:02}:{secs:02}"
        draw_text_with_outline(screen, timer, font, WIDTH - 100, 10, WHITE, BLACK)

        pygame.display.flip()

pygame.quit()
