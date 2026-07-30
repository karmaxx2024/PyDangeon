import pygame
import math
import random

# class Torch(pygame.sprite.Sprite):
#     """Факел на стене с анимированным пламенем"""
#     def __init__(self, x, y, direction='left', wall_side=None):
#         super().__init__()
#         self.x = x
#         self.y = y
#         self.direction = direction
#         self.wall_side = wall_side or ('left' if direction == 'right' else 'right')
#         self.frame = 0
#         self.animation_speed = 0.1

#         self.width = 20
#         self.height = 30

#         self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
#         self.rect = self.image.get_rect()
#         anchor = {
#             'left': 'midright',
#             'right': 'midleft',
#             'top': 'midbottom',
#             'bottom': 'midtop',
#         }.get(self.wall_side, 'center')
#         setattr(self.rect, anchor, (x, y))

#         self.flame_offset = 0
#         self.draw_torch()
        
#     def update(self, dt):
#         """Обновление анимации"""
#         self.frame += self.animation_speed
#         self.flame_offset = math.sin(self.frame * 3) * 3 + math.sin(self.frame * 7) * 1.5
        
#         # Перерисовываем факел
#         self.draw_torch()
        
#     def draw_torch(self):
#         """Рисуем факел геометрическими фигурами"""
#         self.image.fill((0, 0, 0, 0))  # Прозрачный фон
        
#         # Определяем, с какой стороны рисовать
#         if self.direction == 'left':
#             handle_x = 10
#             flame_x = 25
#         else:
#             handle_x = 25
#             flame_x = 10
            
#         # === Деревянная ручка ===
#         # Тень ручки
#         pygame.draw.rect(self.image, (40, 30, 20), 
#                         (handle_x - 2, 25, 10, 30), border_radius=3)
#         # Основная ручка
#         pygame.draw.rect(self.image, (120, 80, 40), 
#                         (handle_x, 20, 6, 35), border_radius=3)
#         # Светлая полоска на ручке
#         pygame.draw.line(self.image, (160, 120, 70), 
#                         (handle_x + 2, 22), (handle_x + 2, 52), 1)
        
#         # === Огонь ===
#         flame_height = 25 + self.flame_offset * 0.5
        
#         # Внешнее свечение (жёлтое)
#         glow_points = [
#             (flame_x, 5 + self.flame_offset * 0.3),
#             (flame_x + 10, 8 + self.flame_offset * 0.5),
#             (flame_x + 12, 15 + self.flame_offset * 0.7),
#             (flame_x + 8, 22 + self.flame_offset * 0.4),
#             (flame_x, 25 + self.flame_offset * 0.2),
#             (flame_x - 8, 22 + self.flame_offset * 0.4),
#             (flame_x - 12, 15 + self.flame_offset * 0.7),
#             (flame_x - 10, 8 + self.flame_offset * 0.5),
#         ]
#         pygame.draw.polygon(self.image, (255, 200, 50), glow_points)
        
#         # Внутреннее пламя (оранжевое)
#         inner_flame = [
#             (flame_x, 10 + self.flame_offset * 0.3),
#             (flame_x + 6, 13 + self.flame_offset * 0.5),
#             (flame_x + 7, 18 + self.flame_offset * 0.6),
#             (flame_x + 4, 22 + self.flame_offset * 0.3),
#             (flame_x, 23 + self.flame_offset * 0.2),
#             (flame_x - 4, 22 + self.flame_offset * 0.3),
#             (flame_x - 7, 18 + self.flame_offset * 0.6),
#             (flame_x - 6, 13 + self.flame_offset * 0.5),
#         ]
#         pygame.draw.polygon(self.image, (255, 120, 20), inner_flame)
        
#         # Ядро пламени (белое)
#         core = [
#             (flame_x, 14 + self.flame_offset * 0.2),
#             (flame_x + 3, 16 + self.flame_offset * 0.3),
#             (flame_x + 3, 19 + self.flame_offset * 0.3),
#             (flame_x, 20 + self.flame_offset * 0.2),
#             (flame_x - 3, 19 + self.flame_offset * 0.3),
#             (flame_x - 3, 16 + self.flame_offset * 0.3),
#         ]
#         pygame.draw.polygon(self.image, (255, 255, 200), core)
        
#         # === Искры ===
#         for i in range(3):
#             spark_x = flame_x + random.randint(-8, 8) + math.sin(self.frame * 5 + i) * 2
#             spark_y = 5 + random.randint(0, 10) + self.flame_offset * 0.3
#             spark_size = random.randint(1, 2)
#             pygame.draw.circle(self.image, (255, 200, 100), 
#                              (int(spark_x), int(spark_y)), spark_size)


class Door(pygame.sprite.Sprite):
    """Дверь с анимацией открытия/закрытия"""
    def __init__(self, x, y, width=50, height=70, is_open=False):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_open = is_open
        self.animation_progress = 1.0 if is_open else 0.0  # 0 = закрыто, 1 = открыто
        self.animation_speed = 4.0  # Скорость анимации
        self.is_animating = False
        
        # Создаём поверхность
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Состояние двери (для коллизий)
        self.is_blocked = not is_open
        self.draw_door()
        
    def toggle(self):
        """Открыть или закрыть дверь"""
        self.is_open = not self.is_open
        self.is_animating = True
        
    def update(self, dt):
        """Обновление анимации"""
        if self.is_animating:
            # Плавное открытие/закрытие
            target = 1.0 if self.is_open else 0.0
            if self.animation_progress < target:
                self.animation_progress = min(1.0, self.animation_progress + self.animation_speed * dt)
                if self.animation_progress >= 1.0:
                    self.is_animating = False
                    self.is_blocked = False
            elif self.animation_progress > target:
                self.animation_progress = max(0.0, self.animation_progress - self.animation_speed * dt)
                if self.animation_progress <= 0.0:
                    self.is_animating = False
                    self.is_blocked = True
            
            self.draw_door()
            
    def draw_door(self):
        """Рисуем дверь"""
        self.image.fill((0, 0, 0, 0))
        
        # Расчёт открытия (поворот вокруг левого края)
        angle = self.animation_progress * 90  # 0° = закрыто, 90° = открыто
        
        # Создаём поверхность для двери с поворотом
        door_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # === Деревянная основа ===
        # Тень двери
        pygame.draw.rect(door_surf, (60, 40, 30), 
                        (5, 5, self.width - 10, self.height - 10), border_radius=4)
        # Основная дверь
        pygame.draw.rect(door_surf, (140, 90, 50), 
                        (2, 2, self.width - 4, self.height - 4), border_radius=4)
        
        # Деревянные доски (горизонтальные линии)
        for i in range(3):
            y_pos = 10 + i * 18
            pygame.draw.line(door_surf, (100, 70, 40), 
                           (8, y_pos), (self.width - 8, y_pos), 2)
            
        # Вертикальная планка
        pygame.draw.line(door_surf, (100, 70, 40), 
                       (self.width // 2, 5), (self.width // 2, self.height - 5), 2)
        
        # === Ручка ===
        # Круглая ручка
        handle_x = self.width - 15
        handle_y = self.height // 2
        pygame.draw.circle(door_surf, (180, 150, 80), (handle_x, handle_y), 5)
        pygame.draw.circle(door_surf, (220, 190, 130), (handle_x - 1, handle_y - 1), 2)
        
        # === Металлические петли ===
        for i in [8, self.height - 8]:
            pygame.draw.rect(door_surf, (100, 100, 100), 
                           (2, i, 8, 4), border_radius=2)
            pygame.draw.rect(door_surf, (60, 60, 60), 
                           (0, i + 1, 4, 2), border_radius=1)
        
        # === Поворот двери (если открыта) ===
        if self.animation_progress > 0.05:
            # Создаём эффект перспективы при открытии
            # (простое сжатие по ширине, имитация поворота)
            scale_x = 1.0 - self.animation_progress * 0.5
            scaled_width = int(self.width * scale_x)
            if scaled_width > 2:
                scaled_surf = pygame.transform.scale(door_surf, (scaled_width, self.height))
                # Смещаем, чтобы левый край оставался на месте
                self.image.blit(scaled_surf, (0, 0))
            else:
                # Полностью открыта - почти не видна
                pass
        else:
            # Закрыта - рисуем полностью
            self.image.blit(door_surf, (0, 0))
        
        # Если дверь полностью открыта, показываем проём
        if self.animation_progress > 0.95:
            # Рисуем тёмный проём
            pygame.draw.rect(self.image, (20, 15, 10), 
                           (2, 2, self.width - 4, self.height - 4), border_radius=4)
            # Сверху рисуем тонкую рамку
            pygame.draw.rect(self.image, (80, 60, 40), 
                           (0, 0, self.width, self.height), 2, border_radius=4)
