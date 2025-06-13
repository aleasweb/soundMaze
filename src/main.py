import pygame
import sys
import math
from maze import MazeGenerator
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Константы
GAME_SHOW = False ### Режим отладки. Видимый лабиринт
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY1 = (100, 100, 100)
GRAY2 = (200, 200, 200)
GREEN2 = (100, 255, 100)
BLUE2 = (150, 200, 255)

class SoundLabGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Звуковой лабиринт")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # Игровые переменные
        self.maze_size = 5  # По умолчанию
        self.maze = None
        self.player_pos = [0, 0]
        self.player_dir = 0  # 0: вверх, 1: вправо, 2: вниз, 3: влево
        self.path = []
        self.game_state = "menu"  # menu/game/end
        self.steps = 0
        self.collisions = 0
        self.collision_points = []
        
        # Загрузка звуков
        self.sounds = {
            "hit": mixer.Sound("assets/sounds/hit.wav"),
            "step": mixer.Sound("assets/sounds/step.wav"),
            "win": mixer.Sound("assets/sounds/win.wav")
        }

        self.last_click_time = 0  # Время последнего клика
        self.click_delay = 300  # Задержка в миллисекундах (0.3 секунды)
    
    def generate_maze(self):
        """Генерирует новый лабиринт"""
        generator = MazeGenerator(self.maze_size, self.maze_size)
        self.maze = generator.generate()
        start, end = generator.get_start_end()
        self.player_pos = list(start)
        self.path = [tuple(self.player_pos)]
        self.steps = 0
        self.collisions = 0
        self.collision_points = []
    
    def handle_movement(self, direction):
        """Обрабатывает движение игрока"""
        if self.maze is None:
            pygame.quit()
            sys.exit()

        dx, dy = 0, 0        
        move_dir = None  # Для запоминания направления движения
    
        # Простые абсолютные направления
        if direction == "forward":  # Вверх
            dy = -1
            move_dir = (0, -1)
        elif direction == "backward":  # Вниз
            dy = 1
            move_dir = (0, 1)
        elif direction == "left":  # Влево
            dx = -1
            move_dir = (-1, 0)
        elif direction == "right":  # Вправо
            dx = 1
            move_dir = (1, 0)

        new_x, new_y = self.player_pos[0] + dx, self.player_pos[1] + dy
        
        # Проверка столкновения
        if (0 <= new_x < self.maze_size and 0 <= new_y < self.maze_size 
            and self.maze[new_y][new_x] == 0):
            self.player_pos = [new_x, new_y]
            self.path.append(tuple(self.player_pos))
            self.steps += 1
            self.sounds["step"].play()
            
            # Проверка победы
            if (new_x, new_y) == (self.maze_size-1, self.maze_size-1):
                self.sounds["win"].play()
                self.game_state = "end"
        else:
            self.collisions += 1
            self.sounds["hit"].play()            
            # Запоминаем точку перед стеной и направление
            self.collision_points.append((tuple(self.player_pos), move_dir))
        
    def draw_menu(self):
        """Отрисовка меню выбора сложности с новым дизайном"""
        self.screen.fill(WHITE)
        
        # Заголовок
        title = self.font.render("Звуковой лабиринт", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # Загрузка изображения лабиринта
        try:
            maze_img = pygame.image.load("assets/img/maze.png")
            maze_img = pygame.transform.scale(maze_img, (300, 300))
            self.screen.blit(maze_img, (50, 100))
        except:
            # Если изображение не найдено, рисуем placeholder
            placeholder = pygame.Surface((300, 300))
            placeholder.fill(GRAY1)
            pygame.draw.rect(placeholder, BLACK, (0, 0, 300, 300), 2)
            self.screen.blit(placeholder, (50, 100))
        
        # Контейнер для выбора уровня
        level_panel = pygame.Rect(SCREEN_WIDTH - 350, 100, 300, 350)
        pygame.draw.rect(self.screen, (240, 240, 240), level_panel, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, level_panel, 2, border_radius=10)
        
        # Заголовок выбора уровня
        level_text = self.font.render("Выберите уровень", True, BLACK)
        self.screen.blit(level_text, (level_panel.x + level_panel.width//2 - level_text.get_width()//2, 
                                    level_panel.y + 20))
        
        # Кнопки уровней
        for i in range(2, 11):
            btn_rect = pygame.Rect(
                level_panel.x + level_panel.width//2 - 100,
                level_panel.y + 50 + (i-2)*30,
                200, 25
            )
            
            # Закругленная кнопка
            pygame.draw.rect(self.screen, (50, 200, 50), btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 1, border_radius=5)
            
            # Текст кнопки
            text = self.font.render(f"{i}x{i}", True, WHITE)
            self.screen.blit(text, (btn_rect.centerx - text.get_width()//2, 
                                    btn_rect.centery - text.get_height()//2))
            
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (100, 255, 100), btn_rect, 2, border_radius=5)
                if pygame.mouse.get_pressed()[0]:
                    self.maze_size = i
        
        # Кнопка старта
        start_btn = pygame.Rect(
            SCREEN_WIDTH//2 - 100,
            level_panel.y + level_panel.height + 20,
            200, 40
        )
        pygame.draw.rect(self.screen, (50, 200, 50), start_btn, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, start_btn, 2, border_radius=8)
        
        start_text = self.font.render("СТАРТ", True, WHITE)
        self.screen.blit(start_text, (start_btn.centerx - start_text.get_width()//2,
                                    start_btn.centery - start_text.get_height()//2))
        
        if start_btn.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (100, 255, 100), start_btn, 3, border_radius=8)
            if pygame.mouse.get_pressed()[0]:
                self.generate_maze()
                self.game_state = "game"
        
        # Отображение выбранного уровня
        selected_text = self.font.render(f"Выбрано: {self.maze_size}x{self.maze_size}", True, BLACK)
        self.screen.blit(selected_text, (SCREEN_WIDTH//2 - selected_text.get_width()//2,
                                        start_btn.y + start_btn.height + 10))
    
    def draw_game(self):
        """Отрисовка игрового экрана с новым дизайном управления"""
        if self.maze is None:
            pygame.quit()
            sys.exit()

        self.screen.fill(WHITE)
        
        # Информационная панель сверху
        info_panel = pygame.Rect(0, 0, SCREEN_WIDTH, 50)
        pygame.draw.rect(self.screen, (240, 240, 240), info_panel)
        pygame.draw.line(self.screen, BLACK, (0, 50), (SCREEN_WIDTH, 50), 2)
        
        # Статистика
        stats_text = f"Уровень: {self.maze_size}x{self.maze_size} | Шаги: {self.steps} | Столкновения: {self.collisions}"
        text_surface = self.font.render(stats_text, True, BLACK)
        self.screen.blit(text_surface, (20, 15))
        
        # Панель управления внизу
        control_panel = pygame.Rect(0, SCREEN_HEIGHT - 180, SCREEN_WIDTH, 180)
        pygame.draw.rect(self.screen, (230, 230, 230), control_panel)
        pygame.draw.line(self.screen, BLACK, (0, SCREEN_HEIGHT-180), (SCREEN_WIDTH, SCREEN_HEIGHT-180), 2)
        
        # Центр крестообразного управления
        center_x, center_y = SCREEN_WIDTH//2, SCREEN_HEIGHT - 90
        btn_size = 50
        btn_padding = 5
        
        # Кнопки управления в виде креста
        controls = [
            ("W", "Вперед", pygame.K_w, (center_x, center_y - btn_size - btn_padding)),
            ("A", "Влево", pygame.K_a, (center_x - btn_size - btn_padding, center_y)),
            ("D", "Вправо", pygame.K_d, (center_x + btn_size + btn_padding, center_y)),
            ("S", "Назад", pygame.K_s, (center_x, center_y + btn_size + btn_padding))
        ]

        # таймер для кнопок управления (от многократного срабатывания)
        current_time = pygame.time.get_ticks()
        
        # Создаем шрифт для символов (может быть больше основного)
        symbol_font = pygame.font.SysFont(None, 36)  # Увеличиваем размер для стрелок
        
        for symbol, text, key, (x, y) in controls:
            btn_rect = pygame.Rect(x - btn_size//2, y - btn_size//2, btn_size, btn_size)
            color = (100, 200, 100) if pygame.key.get_pressed()[key] else (50, 150, 50)
            
            # Закругленная кнопка
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=10)
            
            # Символ на кнопке (используем увеличенный шрифт)
            symbol_surf = symbol_font.render(symbol, True, WHITE)
            self.screen.blit(symbol_surf, (btn_rect.centerx - symbol_surf.get_width()//2,
                                        btn_rect.centery - symbol_surf.get_height()//2))
    
            # Обработка кликов мышкой с задержкой
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (150, 255, 150), btn_rect, 3, border_radius=10)
                if pygame.mouse.get_pressed()[0] and current_time - self.last_click_time > self.click_delay:
                    self.last_click_time = current_time
                    if text == "Вперед":
                        self.handle_movement("forward")
                    elif text == "Назад":
                        self.handle_movement("backward")
                    elif text == "Влево":
                        self.handle_movement("left")
                    elif text == "Вправо":
                        self.handle_movement("right")
        
        # Центральная круглая кнопка (декоративная)
        pygame.draw.circle(self.screen, (180, 180, 180), (center_x, center_y), btn_size//2)
        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), btn_size//2, 2)
        
        # Кнопки действий
        action_btns = [
            ("Сдаюсь", pygame.K_ESCAPE)
        ]
        
        for i, (text, key) in enumerate(action_btns):
            btn_rect = pygame.Rect(SCREEN_WIDTH - 150 if i == 0 else SCREEN_WIDTH - 300, 
                                SCREEN_HEIGHT - 90, 
                                120, 40)
            color = (200, 100, 100) if pygame.key.get_pressed()[key] else (150, 50, 50)
            
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, btn_rect, 2, border_radius=5)
            
            btn_text = self.font.render(text, True, WHITE)
            self.screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2,
                                    btn_rect.centery - btn_text.get_height()//2))


            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (255, 150, 150), btn_rect, 3, border_radius=5)
                if pygame.mouse.get_pressed()[0] and current_time - self.last_click_time > self.click_delay:
                    self.last_click_time = current_time
                    if text == "Сдаюсь":
                        self.game_state = "end"
                    elif text == "Заново":
                        self.generate_maze()
                        self.steps = 0
                        self.collisions = 0
                        self.collision_points = []
        
        # Отрисовка лабиринта (если включен режим отображения)
        if GAME_SHOW:
            self.draw_maze()
        
    
    def draw_end(self):
        """Отрисовка экрана завершения"""        
        self.screen.fill(WHITE)
        self.draw_maze()        
        
        # Очки
        reached_exit = (self.player_pos[0], self.player_pos[1]) == (self.maze_size-1, self.maze_size-1)
        score = (self.maze_size * 100) - (self.steps * 5) - (self.collisions * 10) if reached_exit else 0        
        score_text = self.font.render(f"Очки: {score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 20))
        
        # Кнопка "В меню"
        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, BLUE, btn_rect)
        text = self.font.render("В меню", True, WHITE)
        self.screen.blit(text, (btn_rect.centerx - text.get_width()//2, 
                             btn_rect.centery - text.get_height()//2))
        
        if btn_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.screen, (0, 100, 255), btn_rect, 2)
            if pygame.mouse.get_pressed()[0]:
                self.game_state = "menu"

    def draw_maze(self):
        """Отрисовка лабиринта"""
        if self.maze is None:
            pygame.quit()
            sys.exit()

        maze_width = self.maze_size * CELL_SIZE
        offset_x = (SCREEN_WIDTH - maze_width) // 2
        offset_y = (SCREEN_HEIGHT - maze_width) // 2
        
        # Внешние границы
        border_rect = pygame.Rect(offset_x -1, offset_y -1, maze_width +2, maze_width +2)
        pygame.draw.rect(self.screen, BLACK, border_rect, 2)  # Толщина 2px
        
        # Отрисовка лабиринта (стены и проходы)
        for y in range(self.maze_size):
            for x in range(self.maze_size):
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE,
                    offset_y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                if self.maze[y][x] == 1:  # Стена
                    pygame.draw.rect(self.screen, BLACK, rect)
                else:  # Проход
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
        
        # Маркировка старта и финиша
        start, end = (0, 0), (self.maze_size-1, self.maze_size-1)
        pygame.draw.rect(self.screen, GREEN2,
                        (offset_x + start[0]*CELL_SIZE, 
                        offset_y + start[1]*CELL_SIZE,
                        CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.screen, BLUE2,
                        (offset_x + end[0]*CELL_SIZE,
                        offset_y + end[1]*CELL_SIZE,
                        CELL_SIZE, CELL_SIZE))
        
        # Отрисовка пути
        for i in range(1, len(self.path)):
            x1, y1 = self.path[i-1]
            x2, y2 = self.path[i]
            pygame.draw.line(self.screen, GREEN, 
                            (offset_x + x1*CELL_SIZE + CELL_SIZE//2,
                            offset_y + y1*CELL_SIZE + CELL_SIZE//2),
                            (offset_x + x2*CELL_SIZE + CELL_SIZE//2,
                            offset_y + y2*CELL_SIZE + CELL_SIZE//2), 3)
        
        # Отрисовка точек столкновений с направлением
        for (x, y), (dx, dy) in self.collision_points:
            # Координаты центра текущей клетки
            center_x = offset_x + x*CELL_SIZE + CELL_SIZE//2
            center_y = offset_y + y*CELL_SIZE + CELL_SIZE//2
            
            # Координаты точки перед стеной (половина пути)
            point_x = center_x + dx * CELL_SIZE//2
            point_y = center_y + dy * CELL_SIZE//2
            
            # Отрисовка линии до точки столкновения
            pygame.draw.line(self.screen, GREEN, 
                            (center_x, center_y),
                            (point_x, point_y), 3)
            
            # Отрисовка точки столкновения
            pygame.draw.circle(self.screen, RED,
                            (point_x, point_y),
                            5)  # Радиус 5px
            
        # Отрисовка игрока
        player_rect = pygame.Rect(
            offset_x + self.player_pos[0] * CELL_SIZE + CELL_SIZE//4,
            offset_y + self.player_pos[1] * CELL_SIZE + CELL_SIZE//4,
            CELL_SIZE//2, CELL_SIZE//2
        )
        pygame.draw.rect(self.screen, RED, player_rect)
    
    def run(self):
        """Основной игровой цикл"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == "game" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.handle_movement("forward")
                    elif event.key == pygame.K_s:
                        self.handle_movement("backward")
                    elif event.key == pygame.K_a:
                        self.handle_movement("left")
                    elif event.key == pygame.K_d:
                        self.handle_movement("right")
                    elif event.key == pygame.K_q:
                        self.player_dir = (self.player_dir - 1) % 4
                    elif event.key == pygame.K_e:
                        self.player_dir = (self.player_dir + 1) % 4
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "end"
            
            # Отрисовка
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "game":
                self.draw_game()                
            elif self.game_state == "end":
                self.draw_end()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SoundLabGame()
    game.run()