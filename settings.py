# settings.py
import json
import os
import pygame

# ========== РАЗМЕРЫ ПО УМОЛЧАНИЮ ==========
TILE_SIZE = 32
# Размер лабиринта в тайлах (нечётные числа — требование DFS-генератора)
MAP_WIDTH = 31
MAP_HEIGHT = 21
# Сколько тайлов видно по горизонтали (зум: на большом экране тайлы крупнее)
CAMERA_VIEW_TILES_W = 20
DEFAULT_SCREEN_W = 1280   # <-- добавлено
DEFAULT_SCREEN_H = 720    # <-- добавлено
FPS = 60
PLAYER_SPEED = 300
DEFAULT_PLAYER_SPEED = 300
FLOOR_TILE_WIDTH_MULTIPLIER = 2

# ========== ЦВЕТА ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

UI_DARK_BG = (30, 30, 30)
UI_LIGHT_BG = (240, 240, 240)
UI_ACCENT = (0, 122, 204)
UI_SUCCESS = (34, 197, 94)
UI_WARNING = (234, 179, 8)
UI_ERROR = (239, 68, 68)
UI_TEXT = (20, 20, 20)
UI_TEXT_LG = (245, 245, 245)

GRASS = (34, 139, 34)
SKY = (135, 206, 235)
DIRT = (139, 90, 43)
WATER = (0, 105, 148)
STONE = (112, 128, 144)
SAND = (194, 178, 128)
FOREST_DARK = (0, 76, 0)
SNOW = (255, 250, 250)

FIRE = (255, 69, 0)
ICE = (173, 216, 230)
POISON = (127, 255, 0)
VOID = (75, 0, 130)
GOLD = (255, 215, 0)
NECRO = (0, 255, 127)
BLOOD = (139, 0, 0)
AURA = (100, 149, 237)
SHIELD = (176, 196, 222)

# ========== КЛАСС ДЛЯ РАБОТЫ С НАСТРОЙКАМИ ==========
class GameSettings:
    """Загрузка, сохранение и применение настроек игры"""
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.defaults = {
            "screen_width": 1280,
            "screen_height": 720,
            "fps_limit": 60,
            "master_volume": 0.5,
            "music_volume": 0.5,
            "sfx_volume": 100,
            "fullscreen": False,
            "brightness": 100
        }
        self.load()

    def load(self):
        """Загружает настройки из JSON, при отсутствии создаёт файл с умолчаниями"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                for key in self.defaults:
                    if key in data:
                        setattr(self, key, data[key])
                    else:
                        setattr(self, key, self.defaults[key])
            except Exception as e:
                print(f"Ошибка загрузки config.json: {e}")
                self._set_defaults()
        else:
            self._set_defaults()
            self.save()

    def _set_defaults(self):
        for key, value in self.defaults.items():
            setattr(self, key, value)

    def save(self):
        """Сохраняет текущие настройки в config.json"""
        data = {}
        for key in self.defaults:
            data[key] = getattr(self, key)
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения config.json: {e}")

    def apply_resolution(self, screen):
        """Изменяет размер окна или переключает полноэкранный режим"""
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        new_screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)
        return new_screen

    def get_resolution_options(self):
        """Список доступных разрешений (ширина, высота) с соотношением 16:9"""
        return [
            (1200, 720),
            (1920, 1080),
            (2560, 1440)
        ]

    def set_resolution_by_index(self, index):
        """Устанавливает разрешение по индексу из списка выше"""
        options = self.get_resolution_options()
        if 0 <= index < len(options):
            self.screen_width, self.screen_height = options[index]

    def get_resolution_index(self):
        """Возвращает текущий индекс разрешения в списке"""
        options = self.get_resolution_options()
        current = (self.screen_width, self.screen_height)
        try:
            return options.index(current)
        except ValueError:
            return 0
