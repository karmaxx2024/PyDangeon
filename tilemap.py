import math
import os
import pygame
import random
from settings import *

TILE_WALL = 0
TILE_FLOOR = 1
TILE_DOOR = 2
TILE_STAIRS = 3
TILE_TRAP = 4

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")

WALL_IMAGE = os.path.join(ASSETS_DIR, "decorations", "wall.png")
FLOOR_IMAGE = os.path.join(ASSETS_DIR, "decorations", "floor.jpg")
FLOOR_MOSS_IMAGE = os.path.join(ASSETS_DIR, "decorations", "floor2.jpg")
FLOOR_IMAGE_CANDIDATES = [
    FLOOR_IMAGE,
    os.path.join(ASSETS_DIR, "decoratons", "floor.jpg"),
]
WALL_IMAGE_CANDIDATES = [
    WALL_IMAGE,
    os.path.join(ASSETS_DIR, "decorations", "wall.jpg"),
    os.path.join(ASSETS_DIR, "decoratons", "wall.png"),
    os.path.join(ASSETS_DIR, "decoratons", "wall.jpg"),
]
FLOOR_MOSS_CANDIDATES = [
    FLOOR_MOSS_IMAGE,
    os.path.join(ASSETS_DIR, "decoratons", "floor2.jpg"),
]


def _resolve_asset_path(path, candidates):
    if path and os.path.exists(path):
        return path
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return path or (candidates[0] if candidates else None)


def _resolve_floor_path(path=None):
    """Определяет путь к текстуре пола"""
    if path and os.path.exists(path):
        return path
    if path and "floor2" in path:
        return _resolve_asset_path(path, FLOOR_MOSS_CANDIDATES)
    for candidate in FLOOR_IMAGE_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    decoratons_floor = os.path.join(ASSETS_DIR, "decoratons", "floor.jpg")
    if os.path.exists(decoratons_floor):
        return decoratons_floor
    return path or FLOOR_IMAGE_CANDIDATES[0]


def load_wall_tile(tile_size=TILE_SIZE):
    """Загружает текстуру стены"""
    path = _resolve_asset_path(WALL_IMAGE, WALL_IMAGE_CANDIDATES)
    if not path or not os.path.exists(path):
        print("Нет стены. Искали:", WALL_IMAGE_CANDIDATES)
        return None

    wall_img = pygame.image.load(path)
    if path.lower().endswith(".png"):
        wall_img = wall_img.convert_alpha()
    else:
        wall_img = wall_img.convert()
    print(f"✓ Стена: {path} → тайл {tile_size}x{tile_size}")
    return pygame.transform.scale(wall_img, (tile_size, tile_size))


def load_floor_tile(path=None, tile_size=TILE_SIZE, col=0, row=0):
    """
    Один маленький тайл для замощения экрана.
    - Большая картинка без сетки → ужимаем целиком до tile_size.
    - Лист с сеткой (ширина и высота кратны tile_size) → вырезаем клетку (col, row).
    """
    path = _resolve_floor_path(path)
    if not os.path.exists(path):
        print("Нет пола:", path)
        return None

    sheet = pygame.image.load(path).convert()
    sheet_w, sheet_h = sheet.get_size()

    is_tileset = (
            sheet_w >= tile_size * 2
            and sheet_h >= tile_size * 2
            and sheet_w % tile_size == 0
            and sheet_h % tile_size == 0
    )

    if is_tileset:
        x = col * tile_size
        y = row * tile_size
        tile = sheet.subsurface((x, y, tile_size, tile_size)).copy()
    else:
        tile = pygame.transform.scale(sheet, (tile_size, tile_size))

    print(f"✓ Пол: {path} → тайл {tile.get_size()}")
    return tile


def draw_floor(screen, base_tile, moss_tile=None, layout=None):
    """
    Рисует пол на весь экран (без камеры - для меню и т.д.)
    """
    if not base_tile:
        screen.fill((20, 12, 30))
        return

    sw, sh = screen.get_size()
    tw, th = base_tile.get_size()

    for row, y in enumerate(range(0, sh, th)):
        for col, x in enumerate(range(0, sw, tw)):
            use_moss = (
                    moss_tile is not None
                    and layout is not None
                    and row < len(layout)
                    and col < len(layout[row])
                    and layout[row][col]
            )
            tile = moss_tile if use_moss else base_tile
            screen.blit(tile, (x, y))


def _scale_surface(surface, zoom):
    if zoom == 1.0 or surface is None:
        return surface
    w = max(1, int(surface.get_width() * zoom))
    h = max(1, int(surface.get_height() * zoom))
    return pygame.transform.scale(surface, (w, h))


def draw_floor_with_camera(screen, base_tile, moss_tile, layout, camera_x, camera_y, zoom=1.0):
    """
    Рисует пол с учётом камеры и зума (для основной игры)
    """
    if not base_tile:
        screen.fill((20, 12, 30))
        return

    sw, sh = screen.get_size()
    tw = max(1, int(base_tile.get_width() * zoom))
    th = max(1, int(base_tile.get_height() * zoom))
    base = _scale_surface(base_tile, zoom) if zoom != 1.0 else base_tile
    moss = _scale_surface(moss_tile, zoom) if moss_tile and zoom != 1.0 else moss_tile

    if not layout:
        for y in range(0, sh, th):
            for x in range(0, sw, tw):
                screen.blit(base, (x, y))
        return

    layout_cols = len(layout[0]) if layout else 0
    layout_rows = len(layout) if layout else 0

    start_col = int(math.floor(camera_x / TILE_SIZE))
    end_col = int(math.ceil((camera_x + sw / zoom) / TILE_SIZE))
    start_row = int(math.floor(camera_y / TILE_SIZE))
    end_row = int(math.ceil((camera_y + sh / zoom) / TILE_SIZE))

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            screen_x = (col * TILE_SIZE - camera_x) * zoom
            screen_y = (row * TILE_SIZE - camera_y) * zoom
            if screen_x + tw <= 0 or screen_x >= sw or screen_y + th <= 0 or screen_y >= sh:
                continue

            use_moss = (
                moss is not None
                and 0 <= row < layout_rows
                and 0 <= col < layout_cols
                and layout[row][col]
            )
            screen.blit(moss if use_moss else base, (screen_x, screen_y))


def draw_walls(screen, wall_tile, map_width, map_height, camera_x=0, camera_y=0, show_collision=False, collision_rects=None):
    """
    Рисует стены по периметру карты.
    map_width, map_height - размеры карты в тайлах
    camera_x, camera_y - смещение камеры
    show_collision - показывать ли красные рамки коллизий
    collision_rects - список прямоугольников коллизий для отладки
    """
    if not wall_tile:
        # Если нет текстуры стены, рисуем серые прямоугольники
        wall_color = (80, 80, 80)
        for x in range(map_width):
            for y in range(map_height):
                if x == 0 or x == map_width - 1 or y == 0 or y == map_height - 1:
                    screen_x = x * TILE_SIZE - camera_x
                    screen_y = y * TILE_SIZE - camera_y
                    pygame.draw.rect(screen, wall_color,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        return

    # Рисуем стены по периметру
    for x in range(map_width):
        for y in range(map_height):
            # Если клетка на границе карты - это стена
            if x == 0 or x == map_width - 1 or y == 0 or y == map_height - 1:
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                screen.blit(wall_tile, (screen_x, screen_y))
                
                # Для отладки - показываем красные рамки коллизий
                if show_collision and collision_rects is not None:
                    rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, (255, 0, 0), rect, 2)


def draw_tilemap(screen, floor_tile, wall_tile, map_width, map_height, camera_x=0, camera_y=0, show_collision=False, collision_rects=None):
    """
    Рисует пол и стены на карте.
    Используйте эту функцию для отрисовки всего уровня.
    """
    # Сначала рисуем пол
    draw_floor(screen, floor_tile)
    # Затем рисуем стены поверх
    draw_walls(screen, wall_tile, map_width, map_height, camera_x, camera_y, show_collision, collision_rects)


def generate_floor_layout(screen_w, screen_h, tile_size, moss_chance=0.13):
    """
    Генерирует случайный узор для мха на полу
    """
    cols = (screen_w + tile_size - 1) // tile_size
    rows = (screen_h + tile_size - 1) // tile_size
    return [
        [random.random() < moss_chance for _ in range(cols)]
        for _ in range(rows)
    ]


class CollisionSystem:
    """
    Система коллизий для карты (упрощённая версия)
    Используется для создания коллизий по периметру карты
    """
    def __init__(self, map_width, map_height):
        """
        Создаёт систему коллизий
        
        Args:
            map_width: ширина карты в тайлах
            map_height: высота карты в тайлах
        """
        self.map_width = map_width
        self.map_height = map_height
        self.collision_rects = []
        self._build_collision_map()
    
    def _build_collision_map(self):
        """Создаёт прямоугольники коллизий по периметру карты"""
        self.collision_rects = []
        
        # Стены по периметру
        for x in range(self.map_width):
            for y in range(self.map_height):
                if x == 0 or x == self.map_width - 1 or y == 0 or y == self.map_height - 1:
                    rect = pygame.Rect(
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                    self.collision_rects.append(rect)
        
        print(f"✓ CollisionSystem: создано {len(self.collision_rects)} стен для коллизий")
    
    def check_collision(self, rect, dx, dy):
        """
        Проверяет столкновение при движении
        
        Args:
            rect: прямоугольник игрока
            dx: смещение по X
            dy: смещение по Y
            
        Returns:
            True - есть столкновение, False - можно двигаться
        """
        if not self.collision_rects:
            return False
        
        # Создаём новый прямоугольник после движения
        new_rect = rect.move(dx, dy)
        
        # Проверяем пересечения со стенами
        for wall_rect in self.collision_rects:
            if new_rect.colliderect(wall_rect):
                return True
        return False
    
    def get_collision_rects(self):
        """Возвращает все прямоугольники коллизий (для отладки)"""
        return self.collision_rects
    
    def draw_debug(self, screen, camera_x=0, camera_y=0):
        """
        Рисует красные рамки коллизий для отладки
        """
        for rect in self.collision_rects:
            screen_x = rect.x - camera_x
            screen_y = rect.y - camera_y
            pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, rect.width, rect.height), 2)


class Room:
    """Класс для комнаты в подземелье"""
    
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        """Возвращает центр комнаты"""
        return (self.x + self.w // 2, self.y + self.h // 2)

    def interpects(self, other):
        """Проверяет пересекается ли комната с другой"""
        return (
                self.x <= other.x2 + 1 and
                self.x2 >= other.x - 1 and
                self.y <= other.y2 + 1 and
                self.y2 >= other.y - 1
        )

    def random_floor_point(self):
        """Возвращает случайную точку внутри комнаты"""
        rx = random.randint(self.x + 1, self.x2 - 2)
        ry = random.randint(self.y + 1, self.y2 - 2)
        return rx, ry


class BSPLeaf:
    """Класс для BSP-дерева (Binary Space Partitioning)"""
    MIN_SIZE = 7

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = None
        self.right = None
        self.room = None

    def split(self):
        """
        Разделяет лист на два дочерних
        Returns: True если разделение успешно
        """
        if self.left is not None:
            return False

        # Определяем направление разделения
        if self.w > self.h * 1.25:
            split_horizontal = False
        elif self.h > self.w * 1.25:
            split_horizontal = True
        else:
            split_horizontal = random.choice([True, False])

        if split_horizontal:
            max_split = self.h - self.MIN_SIZE
            if max_split <= self.MIN_SIZE:
                return False
            split_at = random.randint(self.MIN_SIZE, max_split)

            self.left = BSPLeaf(self.x, self.y, self.w, split_at)
            self.right = BSPLeaf(self.x, self.y + split_at, self.w, self.h - split_at)
        else:
            max_split = self.w - self.MIN_SIZE
            if max_split <= self.MIN_SIZE:
                return False
            split_at = random.randint(self.MIN_SIZE, max_split)

            self.left = BSPLeaf(self.x, self.y, split_at, self.h)
            self.right = BSPLeaf(self.x + split_at, self.y, self.w - split_at, self.h)

        return True
    
    def create_rooms(self):
        """
        Создаёт комнаты во всех листьях дерева
        """
        if self.left or self.right:
            if self.left:
                self.left.create_rooms()
            if self.right:
                self.right.create_rooms()
            
            # Создаём коридор между комнатами
            if self.left and self.right and self.left.room and self.right.room:
                self._create_corridor(self.left.room, self.right.room)
        else:
            # Создаём комнату в этом листе
            room_w = random.randint(3, self.w - 2)
            room_h = random.randint(3, self.h - 2)
            room_x = random.randint(self.x, self.x + self.w - room_w)
            room_y = random.randint(self.y, self.y + self.h - room_h)
            self.room = Room(room_x, room_y, room_w, room_h)
    
    def _create_corridor(self, room1, room2):
        """
        Создаёт коридор между двумя комнатами
        """
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        
        # Выбираем случайно: сначала горизонтальный, потом вертикальный или наоборот
        if random.random() < 0.5:
            # Горизонтальный, потом вертикальный
            self._create_horizontal_corridor(x1, x2, y1)
            self._create_vertical_corridor(y1, y2, x2)
        else:
            # Вертикальный, потом горизонтальный
            self._create_vertical_corridor(y1, y2, x1)
            self._create_horizontal_corridor(x1, x2, y2)
    
    def _create_horizontal_corridor(self, x1, x2, y):
        """Создаёт горизонтальный коридор"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            # Здесь можно отметить тайлы как проход
            pass
    
    def _create_vertical_corridor(self, y1, y2, x):
        """Создаёт вертикальный коридор"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            # Здесь можно отметить тайлы как проход
            pass
