import unittest

from src.maze import MazeGenerator

class TestMazeGenerator(unittest.TestCase):
    def setUp(self):
        self.size = 5
        self.maze_gen = MazeGenerator(self.size, self.size)

    def test_generation(self):
        """Проверяет, что лабиринт генерируется корректно."""
        maze = self.maze_gen.generate()
        self.maze_gen.print_maze()
        self.assertEqual(len(maze), self.size)
        self.assertEqual(len(maze[0]), self.size)

        # Проверка входа и выхода
        start, end = self.maze_gen.get_start_end()
        self.maze_gen.print_maze()
        self.assertEqual(maze[start[1]][start[0]], 0)
        self.assertEqual(maze[end[1]][end[0]], 0)

    def test_no_isolated_areas(self):
        """Проверяет, что нет изолированных областей (лабиринт проходим)."""
        maze = self.maze_gen.generate()
        visited = [[False for _ in range(self.size)] for _ in range(self.size)]
        stack = [self.maze_gen.get_start_end()[0]]  # Начинаем с входа

        # DFS для проверки достижимости выхода
        while stack:
            x, y = stack.pop()
            if (x, y) == self.maze_gen.get_start_end()[1]:
                break  # Выход найден
            if visited[y][x]:
                continue
            visited[y][x] = True
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and maze[ny][nx] == 0:
                    stack.append((nx, ny))
        else:
            self.fail("Выход недостижим!")

if __name__ == "__main__":
    unittest.main()