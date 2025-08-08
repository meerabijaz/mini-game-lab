import pygame
import random
import asyncio
import platform
import os

# Initialize Pygame
pygame.init()

# Constants for game settings
GRID_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10  # Starting speed

# Forest-themed color palette
COLORS = {
    'background_dark': (25, 30, 25),  # Very dark forest green
    'background_light': (45, 55, 45), # Lighter dark green
    'grid': (60, 70, 60, 50),        # Faint green grid
    'snake_head': (100, 200, 100),    # Bright green
    'snake_body': (120, 220, 120),    # Lighter green
    'food': (255, 80, 80),            # Red apple
    'food_highlight': (255, 120, 120),# Lighter red for highlight
    'text': (240, 240, 240),          # Off-white text
    'text_shadow': (20, 25, 20),      # Dark shadow for text
    'button_base': (60, 75, 60),      # Muted green button
    'button_border': (30, 40, 30),    # Darker green border
    'button_hover': (90, 110, 90),    # Lighter green hover
    'button_shadow': (10, 15, 10),    # Very dark shadow for 3D effect
}

# Font setup - using a retro, NPC-style font
# Font setup - using a retro, NPC-style font
FONT_PATH = "PressStart2P-Regular.ttf"
try:
    if not os.path.exists(FONT_PATH):
        print(f"Font file '{FONT_PATH}' not found in directory: {os.getcwd()}")
    else:
        print(f"Attempting to load font from: {os.path.abspath(FONT_PATH)}")
        TITLE_FONT = pygame.font.Font(FONT_PATH, 36)
        FONT = pygame.font.Font(FONT_PATH, 20)
        print("Font loaded successfully: Press Start 2P")
except Exception as e:
    print(f"Failed to load font: {e}")
    print("Falling back to Courier New")
    TITLE_FONT = pygame.font.SysFont('couriernew', 36, bold=True)
    FONT = pygame.font.SysFont('couriernew', 20)

# --- Game Classes (Unchanged) ---
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1

    def move(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self):
        self.length += 1

    def collides_with_self(self):
        return self.positions[0] in self.positions[1:]

    def collides_with_wall(self):
        head_x, head_y = self.positions[0]
        return (head_x < 0 or head_x >= GRID_WIDTH or
                head_y < 0 or head_y >= GRID_HEIGHT)

class Food:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        return (random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1))

    def respawn(self, snake_positions):
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            new_pos = self.random_position()
            if new_pos not in snake_positions:
                self.position = new_pos
                return
            attempts += 1
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in snake_positions:
                    self.position = (x, y)
                    return

# --- Enhanced Game Class ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Forest Snake")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.fps = FPS
        self.state = "menu"
        
        # Button positions with improved vertical spacing
        button_width, button_height = 200, 50
        x_pos = (WINDOW_WIDTH - button_width) // 2
        total_button_height = button_height * 2 + 40  # 2 buttons + 40px spacing
        start_y = (WINDOW_HEIGHT - total_button_height) // 2 + 20  # Slight offset for better balance
        
        self.button_rects = {
            "start": pygame.Rect(x_pos, start_y, button_width, button_height),
            "exit": pygame.Rect(x_pos, start_y + button_height + 40, button_width, button_height),
            "retry": pygame.Rect(x_pos, start_y, button_width, button_height),
            "main_menu": pygame.Rect(x_pos, start_y + button_height + 40, button_width, button_height),
        }
        self.hovered_button = None

    def draw_background(self):
        # Gradient background
        for i in range(WINDOW_HEIGHT):
            color = (
                COLORS['background_dark'][0] + (COLORS['background_light'][0] - COLORS['background_dark'][0]) * i // WINDOW_HEIGHT,
                COLORS['background_dark'][1] + (COLORS['background_light'][1] - COLORS['background_dark'][1]) * i // WINDOW_HEIGHT,
                COLORS['background_dark'][2] + (COLORS['background_light'][2] - COLORS['background_dark'][2]) * i // WINDOW_HEIGHT
            )
            pygame.draw.line(self.screen, color, (0, i), (WINDOW_WIDTH, i))

    def draw_grid(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(surface, COLORS['grid'], (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, COLORS['grid'], (0, y), (WINDOW_WIDTH, y), 1)
        self.screen.blit(surface, (0, 0))

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.positions):
            center_x = x * CELL_SIZE + CELL_SIZE // 2
            center_y = y * CELL_SIZE + CELL_SIZE // 2
            if i == 0:
                pygame.draw.circle(self.screen, COLORS['snake_head'],
                                   (center_x, center_y), CELL_SIZE // 2 - 2)
                # Eyes
                pygame.draw.circle(self.screen, (0, 0, 0), (center_x - 4, center_y - 3), 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (center_x + 4, center_y - 3), 2)
                pygame.draw.circle(self.screen, (255, 255, 255), (center_x - 4, center_y - 3), 1)
                pygame.draw.circle(self.screen, (255, 255, 255), (center_x + 4, center_y - 3), 1)
            else:
                pygame.draw.circle(self.screen, COLORS['snake_body'],
                                   (center_x, center_y), CELL_SIZE // 2 - 3)

    def draw_food(self):
        center_x = self.food.position[0] * CELL_SIZE + CELL_SIZE // 2
        center_y = self.food.position[1] * CELL_SIZE + CELL_SIZE // 2
        # Apple body
        pygame.draw.circle(self.screen, COLORS['food'], (center_x, center_y), CELL_SIZE // 2 - 2)
        # Highlight
        pygame.draw.circle(self.screen, COLORS['food_highlight'], (center_x - 2, center_y - 3), 3)
        # Stem
        pygame.draw.rect(self.screen, COLORS['button_border'], (center_x - 1, center_y - 8, 2, 5))
    
    def draw_text(self, text, font, color, center_x, center_y, shadow=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        
        if shadow:
            shadow_surface = font.render(text, True, COLORS['text_shadow'])
            shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
            self.screen.blit(shadow_surface, shadow_rect)
        
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, text, rect, is_hovered):
        color = COLORS['button_hover'] if is_hovered else COLORS['button_base']
        pygame.draw.rect(self.screen, COLORS['button_shadow'], (rect.x + 4, rect.y + 4, rect.width, rect.height), border_radius=12)
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, COLORS['button_border'], rect, 2, border_radius=12)
        
        self.draw_text(text, FONT, COLORS['text'], rect.centerx, rect.centery, shadow=False)

    def draw_menu(self):
        self.draw_background()
        self.draw_grid()
        
        # Adjusted title position for better balance
        self.draw_text("Forest Snake", TITLE_FONT, COLORS['text'], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 5)
        
        self.draw_button("Start Game", self.button_rects["start"], self.hovered_button == "start")
        self.draw_button("Exit", self.button_rects["exit"], self.hovered_button == "exit")

    def draw_game_over(self):
        self.draw_background()
        self.draw_grid()
        
        # Adjusted game over text positions
        self.draw_text("Game Over!", TITLE_FONT, COLORS['text'], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 5)
        self.draw_text(f"Score: {self.score}", FONT, COLORS['text'], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)
        
        self.draw_button("Retry", self.button_rects["retry"], self.hovered_button == "retry")
        self.draw_button("Main Menu", self.button_rects["main_menu"], self.hovered_button == "main_menu")

    def draw_game(self):
        self.draw_background()
        self.draw_grid()
        self.draw_snake()
        self.draw_food()
        
        # Score positioned with slight padding
        self.draw_text(f"Score: {self.score}", FONT, COLORS['text'], 80, 30, shadow=True)

    def run(self):
        running = True
        self.state = "menu"
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == "playing":
                        if event.key in (pygame.K_UP, pygame.K_w) and self.snake.direction != (0, 1):
                            self.snake.direction = (0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.snake.direction != (0, -1):
                            self.snake.direction = (0, 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a) and self.snake.direction != (1, 0):
                            self.snake.direction = (-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.snake.direction != (-1, 0):
                            self.snake.direction = (1, 0)
                elif event.type == pygame.MOUSEMOTION:
                    self.hovered_button = None
                    for button, rect in self.button_rects.items():
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            self.hovered_button = button
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button, rect in self.button_rects.items():
                            if rect.collidepoint(event.pos):
                                if self.state == "menu":
                                    if button == "start":
                                        self.state = "playing"
                                        self.snake.reset()
                                        self.food.respawn(self.snake.positions)
                                        self.score = 0
                                    elif button == "exit":
                                        running = False
                                elif self.state == "game_over":
                                    if button == "retry":
                                        self.state = "playing"
                                        self.snake.reset()
                                        self.food.respawn(self.snake.positions)
                                        self.score = 0
                                    elif button == "main_menu":
                                        self.state = "menu"
            
            if self.state == "playing":
                self.snake.move()
                if self.snake.positions[0] == self.food.position:
                    self.snake.grow()
                    self.food.respawn(self.snake.positions)
                    self.score += 10
                if self.snake.collides_with_self() or self.snake.collides_with_wall():
                    self.state = "game_over"

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(self.fps)

    async def main(self):
        self.run()

if platform.system() == "Emscripten":
    game = Game()
    asyncio.run(game.main())
else:
    if __name__ == "__main__":
        game = Game()
        game.run()