class SoundMazeGame {
    constructor() {
        this.maze_size = 5;
        this.maze = null;
        this.player_pos = [0, 0];
        this.steps = 0;
        this.collisions = 0;
        this.game_state = "menu";
        this.path = []; // Добавляем сохранение пути
        this.path.push([...this.player_pos])
        this.collision_points = []; // Точки столкновений

        this.sounds = {
            step: new Audio('assets/sounds/step.wav'),
            hit: new Audio('assets/sounds/hit.wav'),
            win: new Audio('assets/sounds/win.wav')                    
        };
        
        // Настройка звуков
        Object.values(this.sounds).forEach(sound => {
            sound.preload = 'auto';
            sound.volume = 0.7; // Установите подходящую громкость
        });
        
        this.soundEnabled = true; // Флаг для включения/выключения звука
        
        this.initElements();
        this.bindEvents();
    }
    
    initElements() {
        
        // Получаем элементы экранов
        this.menuScreen = document.querySelector('.menu-screen');
        this.gameScreen = document.querySelector('.game-screen');
        
        // Проверяем, что элементы найдены
        if (!this.menuScreen || !this.gameScreen) {
            console.error('Не найдены элементы экранов!');
            return;
        }

        // Инициализируем начальное состояние
        this.menuScreen.style.display = 'flex';
        this.gameScreen.style.display = 'none';

        this.levelButtons = document.querySelectorAll('.level-btn');
        this.levelInfo = document.getElementById('level-info');
        this.stepsDisplay = document.getElementById('steps');
        this.collisionsDisplay = document.getElementById('collisions');
        
        this.forwardBtn = document.getElementById('forward-btn');
        this.leftBtn = document.getElementById('left-btn');
        this.rightBtn = document.getElementById('right-btn');
        this.backwardBtn = document.getElementById('backward-btn');
        this.giveUpBtn = document.getElementById('give-up-btn');
    }
    
    bindEvents() {
        this.levelButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.maze_size = parseInt(btn.dataset.size);
                this.startGame();
            });
        });
        
        this.forwardBtn.addEventListener('click', () => this.handleMovement('forward'));
        this.leftBtn.addEventListener('click', () => this.handleMovement('left'));
        this.rightBtn.addEventListener('click', () => this.handleMovement('right'));
        this.backwardBtn.addEventListener('click', () => this.handleMovement('backward'));
        this.giveUpBtn.addEventListener('click', () => this.endGame());
    }
    
    startGame() {
        // Генерация лабиринта
        const generator = new MazeGenerator(this.maze_size, this.maze_size);
        this.maze = generator.generate();
        this.player_pos = [0, 0];
        this.steps = 0;
        this.collisions = 0;
        this.path = [];
        this.path.push([...this.player_pos])
        this.collision_points = [];
        
        // Обновление интерфейса
        this.levelInfo.textContent = `Уровень: ${this.maze_size}×${this.maze_size}`;
        this.stepsDisplay.textContent = `Шаги: ${this.steps}`;
        this.collisionsDisplay.textContent = `Столкновения: ${this.collisions}`;

        // Переключаем экраны
        try {
            this.menuScreen.style.display = 'none';
            this.gameScreen.style.display = 'flex';
        } catch (e) {
            console.error('Ошибка при переключении экранов:', e);
        }
    }
    
    handleMovement(direction) {
        if (!this.maze) return;
        
        let dx = 0, dy = 0;
        let move_dir = null; // Направление движения для столкновений
        
        switch(direction) {
            case 'forward': 
                dy = -1; 
                move_dir = [0, -1];
                break;
            case 'backward': 
                dy = 1; 
                move_dir = [0, 1];
                break;
            case 'left': 
                dx = -1; 
                move_dir = [-1, 0];
                break;
            case 'right': 
                dx = 1; 
                move_dir = [1, 0];
                break;
        }
        
        const new_x = this.player_pos[0] + dx;
        const new_y = this.player_pos[1] + dy;
        
        if (new_x >= 0 && new_x < this.maze_size && 
            new_y >= 0 && new_y < this.maze_size && 
            this.maze[new_y][new_x] === 0) {
            
            this.player_pos = [new_x, new_y];
            this.path.push([...this.player_pos]); // Сохраняем путь
            this.steps++;
            this.stepsDisplay.textContent = `Шаги: ${this.steps}`;
            
            // Воспроизведение звука шага
            if (this.soundEnabled) {
                this.sounds.step.currentTime = 0;
                this.sounds.step.play();
            }
            
            // Проверка победы
            if (new_x === this.maze_size-1 && new_y === this.maze_size-1) {
                if (this.soundEnabled) {
                    this.sounds.win.currentTime = 0;
                    this.sounds.win.play();
                }
                this.showResults(true);
            }
        } else {
            this.collisions++;
            this.collision_points.push([[...this.player_pos], move_dir]); // Сохраняем столкновение
            this.collisionsDisplay.textContent = `Столкновения: ${this.collisions}`;
            // Воспроизведение звука столкновения
            if (this.soundEnabled) {
                this.sounds.hit.currentTime = 0;
                this.sounds.hit.play();
            }
        }
    }
    
    showResults(reached_exit) {
        // Переключаем на экран результатов
        this.gameScreen.style.display = 'none';
        this.menuScreen.style.display = 'none';
        document.querySelector('.result-screen').style.display = 'flex';
        
        // Отрисовываем лабиринт
        this.drawMazeHTML();
        
        // Обновляем информацию о результатах
        const score = reached_exit ? 
            (this.maze_size * 100) - (this.steps * 5) - (this.collisions * 10) : 0;
        
        document.getElementById('result-title').textContent = 
            reached_exit ? 'Поздравляем!' : 'Игра окончена';
        document.getElementById('result-text').textContent = reached_exit ? 
            `Вы прошли лабиринт ${this.maze_size}×${this.maze_size}` : 
            `Вы не достигли выхода (${this.maze_size}×${this.maze_size})`;
        document.getElementById('result-score').textContent = `Очки: ${score}`;
        document.getElementById('result-score').className = 
            reached_exit ? 'score-display success' : 'score-display error';
    }
    
    drawMazeHTML() {
        const container = document.getElementById('maze-container');
        container.innerHTML = '';
        
        const mazeSize = this.maze_size;
        const cellSize = Math.min(300 / mazeSize, 60); // Автоподбор размера клетки
        
        // Создаем SVG элемент для лабиринта
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', `0 0 ${mazeSize * cellSize} ${mazeSize * cellSize}`);
        
        // Отрисовка стен и проходов
        for (let y = 0; y < mazeSize; y++) {
            for (let x = 0; x < mazeSize; x++) {
                const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                rect.setAttribute('x', x * cellSize);
                rect.setAttribute('y', y * cellSize);
                rect.setAttribute('width', cellSize);
                rect.setAttribute('height', cellSize);
                
                if (this.maze[y][x] === 1) { // Стена
                    rect.setAttribute('fill', 'var(--md-on-surface)');
                } else { // Проход
                    rect.setAttribute('fill', 'var(--md-surface)');
                    rect.setAttribute('stroke', 'var(--md-outline)');
                    rect.setAttribute('stroke-width', '0.5');
                }
                
                svg.appendChild(rect);
            }
        }

        // Стартовая точка
        const start = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        start.setAttribute('x', 0);
        start.setAttribute('y', 0);
        start.setAttribute('width', cellSize);
        start.setAttribute('height', cellSize);
        start.setAttribute('fill', '#81B29A');
        svg.appendChild(start);
        
        // Конечная точка
        const end = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        end.setAttribute('x', (mazeSize-1) * cellSize);
        end.setAttribute('y', (mazeSize-1) * cellSize);
        end.setAttribute('width', cellSize);
        end.setAttribute('height', cellSize);
        end.setAttribute('fill', '#F2CC8F');
        svg.appendChild(end);
        
        // Отрисовка пути
        if (this.path.length > 1) {
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            let d = `M ${this.path[0][0] * cellSize + cellSize/2} ${this.path[0][1] * cellSize + cellSize/2}`;
            
            for (let i = 1; i < this.path.length; i++) {
                d += ` L ${this.path[i][0] * cellSize + cellSize/2} ${this.path[i][1] * cellSize + cellSize/2}`;
            }
            
            path.setAttribute('d', d);
            path.setAttribute('stroke', 'var(--path-color)');
            path.setAttribute('stroke-width', '3');
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke-linecap', 'round');
            path.setAttribute('stroke-linejoin', 'round');
            svg.appendChild(path);
        }
        
        // Отрисовка точек столкновений
        this.collision_points.forEach(([[x, y], [dx, dy]]) => {
            const centerX = x * cellSize + cellSize/2;
            const centerY = y * cellSize + cellSize/2;
            const endX = centerX + dx * cellSize/2;
            const endY = centerY + dy * cellSize/2;
            
            // Линия столкновения
            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute('x1', centerX);
            line.setAttribute('y1', centerY);
            line.setAttribute('x2', endX);
            line.setAttribute('y2', endY);
            line.setAttribute('stroke', 'var(--collision-color)');
            line.setAttribute('stroke-width', '2');
            svg.appendChild(line);
            
            // Точка столкновения
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute('cx', endX);
            circle.setAttribute('cy', endY);
            circle.setAttribute('r', '3');
            circle.setAttribute('fill', 'var(--collision-color)');
            svg.appendChild(circle);
        });
        
        // Позиция игрока
        const player = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        player.setAttribute('x', this.player_pos[0] * cellSize + cellSize/4);
        player.setAttribute('y', this.player_pos[1] * cellSize + cellSize/4);
        player.setAttribute('width', cellSize/2);
        player.setAttribute('height', cellSize/2);
        player.setAttribute('fill', 'var(--collision-color)');
        svg.appendChild(player);
        
        container.appendChild(svg);
    }
    
    createCell(x, y, size, color) {
        const cell = document.createElement('div');
        cell.style.position = 'absolute';
        cell.style.left = `${x * size}px`;
        cell.style.top = `${y * size}px`;
        cell.style.width = `${size}px`;
        cell.style.height = `${size}px`;
        cell.style.backgroundColor = color;
        return cell;
    }
    
    endGame() {
        this.showResults(false);
    }
}

function drawMazeHTML(maze, mazeSize, cellSize, path, playerPos, collisions) {
    const container = document.getElementById('maze-container');
    container.innerHTML = '';
    
    const mazeWidth = mazeSize * cellSize;
    const offsetX = (container.clientWidth - mazeWidth) / 2;
    const offsetY = (container.clientHeight - mazeWidth) / 2;
    
    // Создаем элемент лабиринта
    const mazeElement = document.createElement('div');
    mazeElement.style.position = 'absolute';
    mazeElement.style.left = `${offsetX}px`;
    mazeElement.style.top = `${offsetY}px`;
    mazeElement.style.width = `${mazeWidth}px`;
    mazeElement.style.height = `${mazeWidth}px`;
    mazeElement.style.border = '2px solid #000';
    
    // Отрисовка клеток лабиринта
    for (let y = 0; y < mazeSize; y++) {
        for (let x = 0; x < mazeSize; x++) {
        const cell = document.createElement('div');
        cell.style.position = 'absolute';
        cell.style.left = `${x * cellSize}px`;
        cell.style.top = `${y * cellSize}px`;
        cell.style.width = `${cellSize}px`;
        cell.style.height = `${cellSize}px`;
        
        if (maze[y][x] === 1) { // Стена
            cell.style.backgroundColor = '#000';
        } else { // Проход
            cell.style.backgroundColor = '#FFF';
            cell.style.border = '1px solid #DDD';
        }
        
        mazeElement.appendChild(cell);
        }
    }
    
    // Старт и финиш
    const start = createCell(0, 0, '#81B29A');
    const finish = createCell(mazeSize-1, mazeSize-1, '#F2CC8F');
    mazeElement.appendChild(start);
    mazeElement.appendChild(finish);
    
    // Путь игрока
    if (path && path.length > 1) {
        const pathElement = document.createElement('div');
        pathElement.style.position = 'absolute';
        pathElement.style.width = '3px';
        pathElement.style.backgroundColor = '#388E3C';
        pathElement.style.zIndex = '1';
        
        for (let i = 1; i < path.length; i++) {
        const [x1, y1] = path[i-1];
        const [x2, y2] = path[i];
        
        const line = pathElement.cloneNode();
        const length = Math.sqrt(Math.pow((x2-x1)*cellSize, 2) + Math.pow((y2-y1)*cellSize, 2));
        const angle = Math.atan2((y2-y1)*cellSize, (x2-x1)*cellSize) * 180 / Math.PI;
        
        line.style.left = `${x1 * cellSize + cellSize/2}px`;
        line.style.top = `${y1 * cellSize + cellSize/2}px`;
        line.style.width = `${length}px`;
        line.style.height = '3px';
        line.style.transformOrigin = '0 50%';
        line.style.transform = `rotate(${angle}deg)`;
        
        mazeElement.appendChild(line);
        }
    }
    
    // Игрок
    const player = createCell(playerPos[0], playerPos[1], '#D32F2F');
    player.style.zIndex = '2';
    mazeElement.appendChild(player);
    
    container.appendChild(mazeElement);
    
    function createCell(x, y, color) {
        const cell = document.createElement('div');
        cell.style.position = 'absolute';
        cell.style.left = `${x * cellSize}px`;
        cell.style.top = `${y * cellSize}px`;
        cell.style.width = `${cellSize}px`;
        cell.style.height = `${cellSize}px`;
        cell.style.backgroundColor = color;
        return cell;
    }
}