class MazeGenerator {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.maze = Array(height).fill().map(() => Array(width).fill(1));
    }

    isMazePassable() {
        // Проверяем, что старт и финиш - проходимые клетки
        if (this.maze[0][0] !== 0 || this.maze[this.height-1][this.width-1] !== 0) {
            return false;
        }

        const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]; // Вниз, вправо, вверх, влево
        const visited = Array(this.height).fill().map(() => Array(this.width).fill(false));
        const queue = [[0, 0]]; // Начинаем с стартовой позиции
        visited[0][0] = true;

        while (queue.length > 0) {
            const [x, y] = queue.shift();

            // Если достигли финиша
            if (x === this.width-1 && y === this.height-1) {
                return true;
            }

            // Проверяем все соседние клетки
            for (const [dx, dy] of directions) {
                const nx = x + dx;
                const ny = y + dy;

                // Проверяем границы лабиринта и что клетка проходима
                if (nx >= 0 && nx < this.width && 
                    ny >= 0 && ny < this.height && 
                    this.maze[ny][nx] === 0 && 
                    !visited[ny][nx]) {
                    
                    visited[ny][nx] = true;
                    queue.push([nx, ny]);
                }
            }
        }

        return false; // Если дошли сюда - путь не найден
    }

    generate() {
        do {
            // Генерируем лабиринт (ваш существующий код)
            const start_x = 0, start_y = 0;
            this.maze = Array(this.height).fill().map(() => Array(this.width).fill(1));
            this.maze[start_y][start_x] = 0;
            let walls = this._get_walls(start_x, start_y);

            while (walls.length > 0) {
                const randomIndex = Math.floor(Math.random() * walls.length);
                const [wall_x, wall_y] = walls[randomIndex];
                walls.splice(randomIndex, 1);

                if (this._is_valid_wall(wall_x, wall_y)) {
                    this.maze[wall_y][wall_x] = 0;
                    walls.push(...this._get_walls(wall_x, wall_y));
                }
            }

            // Гарантируем, что выход проходим
            this.maze[this.height - 1][this.width - 1] = 0;
        } while (!this.isMazePassable()); // Повторяем пока лабиринт не станет проходимым

        return this.maze;
    }

    _get_walls(x, y) {
        const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];
        const walls = [];
        
        for (const [dx, dy] of directions) {
            const nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height && this.maze[ny][nx] === 1) {
                walls.push([nx, ny]);
            }
        }
        return walls;
    }

    _is_valid_wall(x, y) {
        const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];
        let passages = 0;
        
        for (const [dx, dy] of directions) {
            const nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height && this.maze[ny][nx] === 0) {
                passages += 1;
                if (passages > 1) return false;
            }
        }
        return passages === 1;
    }
}