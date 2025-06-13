import random
from typing import List, Tuple

class MazeGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]  # 1 = стена, 0 = проход

    def generate(self) -> List[List[int]]:
        """Генерирует лабиринт с входом (0, 0) и выходом (w-1, h-1)."""
        # Начальная точка (от нее строим лабиринт)
        start_x, start_y = 0, 0
        self.maze[start_y][start_x] = 0
        walls = self._get_walls(start_x, start_y)

        while walls:
            # Выбираем случайную стену
            wall_x, wall_y = random.choice(walls)
            walls.remove((wall_x, wall_y))

            # Проверяем, можно ли превратить стену в проход
            if self._is_valid_wall(wall_x, wall_y):
                self.maze[wall_y][wall_x] = 0
                walls.extend(self._get_walls(wall_x, wall_y))

        # Гарантируем, что выход (w-1, h-1) проходим
        self.maze[self.height - 1][self.width - 1] = 0

        ## Фикс алгоритма для закрытого выхода
        if self.maze[self.height - 1][self.width - 2] == 1 and self.maze[self.height - 2][self.width - 1] == 1:
            self.maze[self.height - 1][self.width - 2] = 0
            self.maze[self.height - 2][self.width - 1] = 0

        return self.maze

    def _get_walls(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Возвращает список соседних стен для клетки (x, y)."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        walls = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] == 1:
                walls.append((nx, ny))
        return walls

    def _is_valid_wall(self, x: int, y: int) -> bool:
        """Проверяет, можно ли превратить стену (x, y) в проход."""
        # Считаем количество соседних проходов
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        passages = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] == 0:
                passages += 1
                if passages > 1:
                    return False  # Нельзя создать петлю
        return passages == 1  # Только 1 соседний проход

    def get_start_end(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Возвращает координаты входа (0, 0) и выхода (w-1, h-1)."""
        return (0, 0), (self.width - 1, self.height - 1)