"""Игра 'Змейка' на Pygame"""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 8

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс игрового объекта.

    Хранит общие данные: поверхность для отрисовки (surface),
    позицию на поле (position) и цвет (body_color).
    """

    def __init__(
            self,
            body_color: tuple[int, int, int],
            surface=screen
    ):
        self.surface = surface
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color: tuple[int, int, int] = body_color

    def draw(self) -> None:
        """
        Отрисовывает объект на поверхности.
        Переопределяется в наследниках.
        """
        pass


class Apple(GameObject):
    """Яблоко — цель змейки.

    При создании занимает случайную **свободную** клетку поля; после поедания
    перегенерируется на новой свободной клетке.
    """

    def __init__(
            self,
            body_color: tuple[int, int, int] = APPLE_COLOR
    ):
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self, snake_positions=()) -> None:
        """Размещает яблоко на случайной клетке, не занятой змейкой.

        Координаты перегенерируются, пока не выпадет клетка вне
        snake_positions. По умолчанию проверка пропускается.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in snake_positions:
                break

    def draw(self) -> None:
        """Рисует яблоко: заливка цветом яблока и контур BORDER_COLOR."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.surface, self.body_color, rect)
        pygame.draw.rect(self.surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка — управляемый игроком объект.

    Сегменты хранятся в positions, голова — первый элемент списка.
    Отдельно хранятся длина (length), текущее и буферизованное
    направления (direction, next_direction) и клетка, с которой
    уполз хвост (last).
    """

    def reset(self) -> None:
        """Возвращает змейку в начальное состояние после столкновения.

        Длина — 1, один сегмент в центре поля, случайное направление.
        """
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction: tuple[int, int] | None = None
        self.last: tuple[int, int] | None = None

    def __init__(
            self,
            body_color: tuple[int, int, int] = SNAKE_COLOR
    ):
        super().__init__(body_color)
        self.reset()

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает координаты головы — первого элемента positions."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Копирует next_direction в direction и сбрасывает в None."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Сдвигает змейку на одну клетку в текущем направлении.

        Новая голова добавляется в начало списка; если список длиннее
        length, хвостовой сегмент удаляется и запоминается в last.
        Выход за границы поля включается зацикливанием по модулю.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку и затирает клетку покинутого хвоста.

        Затирание выполняется ДО отрисовки: в кольцевом движении новая
        голова встаёт на клетку last, и затирание после отрисовки
        стирало бы голову.
        """
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(self.surface, BOARD_BACKGROUND_COLOR, last_rect)

        # Тело — все сегменты, кроме головы
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(self.surface, self.body_color, rect)
            pygame.draw.rect(self.surface, BORDER_COLOR, rect, 1)

        # Голова — первый элемент списка
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.surface, self.body_color, head_rect)
        pygame.draw.rect(self.surface, BORDER_COLOR, head_rect, 1)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает события клавиатуры и закрытия окна.

    Стрелки записывают желаемое направление в next_direction —
    кроме разворота на 180 градусов. pygame.QUIT завершает игру.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной игровой цикл.

    На каждой итерации: ограничение скорости, обработка ввода,
    движение, проверки поедания яблока и самостолкновения,
    отрисовка и обновление экрана.
    """
    # Инициализация PyGame:
    pygame.init()

    # Создаём игровые объекты.
    snake = Snake(SNAKE_COLOR)
    apple = Apple(APPLE_COLOR)
    apple.randomize_position(snake.positions)  # первое яблоко не в змейке

    while True:
        clock.tick(SPEED)

        # Обработка ввода и обновление направления
        handle_keys(snake)
        snake.update_direction()

        # Движение змейки.
        snake.move()

        # Проверяем, съела ли змейка яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Проверяем, не столкнулась ли змейка с собой.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Отрисовка объектов.
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
