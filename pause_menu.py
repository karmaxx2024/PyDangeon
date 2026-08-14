import os
import pygame
import colorsys
from settings import *

# Папка со шрифтами
base_path = os.path.join("assets", "fonts")


class PauseMenu:
    """Меню паузы с остановкой игрового процесса"""

    def __init__(self, screen):
        self.screen = screen
        self.is_paused = False
        self.selected_option = 0
        self.options = ["Продолжить", "Сохранить", "Настройки", "В главное меню", "Выход"]  # <-- добавлен "Сохранить"
        self.option_rects = []
        
        # Для анимации переливания
        self.hover_hue = 0.0  # оттенок для переливания (0-1)
        self.hover_timer = 0.0

        # Шрифты
        try:
            self.font_title = pygame.font.Font(
                os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf"), 72
            )
            self.font_normal = pygame.font.Font(
                os.path.join(base_path, "Philosopher-Bold.ttf"), 48
            )
            self.hint_font = pygame.font.Font(
                os.path.join(base_path, "Philosopher-Bold.ttf"), 24
            )
        except Exception:
            self.font_title = pygame.font.SysFont("Arial", 72)
            self.font_normal = pygame.font.SysFont("Arial", 48)
            self.hint_font = pygame.font.SysFont("Arial", 24)

        # Полупрозрачная поверхность
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))

        # ===== ЗАГРУЗКА КАСТОМНОГО КУРСОРА (как в menu.py и character_selection.py) =====
        try:
            self.cursor_hover = pygame.image.load("assets/images/menu/mouse2.png").convert_alpha()
            self.cursor_hover = pygame.transform.smoothscale(self.cursor_hover, (64, 64))
            self.cursor = pygame.image.load("assets/images/menu/mouse1.png").convert_alpha()
            self.cursor = pygame.transform.smoothscale(self.cursor, (64, 64))
        except Exception as e:
            print(f"Ошибка загрузки курсора в PauseMenu: {e}")
            self.cursor = None
            self.cursor_hover = None
        pygame.mouse.set_visible(False)   # скрываем системный курсор
        # ===========================================

        print("✓ PauseMenu готов")

    def update_screen(self, screen):
        """Обновить размеры после смены разрешения."""
        self.screen = screen
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))

    def toggle(self):
        """Переключает состояние паузы"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            print("⏸ Игра на паузе")
        else:
            print("▶ Игра продолжена")

        return self.is_paused

    def handle_input(self, events):
        """
        Обрабатывает ввод в меню паузы.
        Returns:
            None, "resume", "save", "settings", "menu", "quit"
        """
        if not self.is_paused:
            return None

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"

                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)

                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)

                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        return "resume"
                    elif self.selected_option == 1:
                        return "save"          # <-- добавлен возврат "save"
                    elif self.selected_option == 2:
                        return "settings"
                    elif self.selected_option == 3:
                        return "menu"
                    elif self.selected_option == 4:
                        return "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_option = i

                            if i == 0:
                                return "resume"
                            elif i == 1:
                                return "save"          # <-- добавлен возврат "save"
                            elif i == 2:
                                return "settings"
                            elif i == 3:
                                return "menu"
                            elif i == 4:
                                return "quit"

        return None

    def get_rainbow_color(self):
        """Возвращает цвет переливания: красный -> оранжевый -> жёлтый"""
        hue = 0.16 * (0.5 + 0.5 * __import__('math').sin(self.hover_timer * 2.0))
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    def draw(self):
        """Рисует меню паузы"""
        if not self.is_paused:
            return

        # Обновляем таймер анимации
        self.hover_timer += 0.05  # скорость переливания
        
        sw, sh = self.screen.get_width(), self.screen.get_height()

        # Затемнённый фон
        self.screen.blit(self.overlay, (0, 0))

        # Заголовок
        title_text = self.font_title.render("ПАУЗА", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(sw // 2, sh // 4))
        self.screen.blit(title_text, title_rect)

        # Пункты меню
        self.option_rects.clear()
        mouse_pos = pygame.mouse.get_pos()
        
        # Проверяем, наведена ли мышь на какую-либо кнопку
        mouse_over_any = False

        for i, option in enumerate(self.options):
            # Сначала создаём временный прямоугольник для проверки коллизии
            temp_text = self.font_normal.render(option, True, (255, 255, 255))
            rect = temp_text.get_rect(center=(sw // 2, sh // 2 + i * 60))
            self.option_rects.append(rect)

            if rect.collidepoint(mouse_pos):
                self.selected_option = i
                mouse_over_any = True

            # Выбираем цвет для кнопки
            if i == self.selected_option:
                if mouse_over_any and i == self.selected_option:
                    # Переливающийся цвет при наведении мыши
                    color = self.get_rainbow_color()
                else:
                    # Обычный жёлтый для выбранной кнопки (клавиатура)
                    color = (255, 255, 0)
            else:
                # Серый для невыбранных кнопок
                color = (200, 200, 200)

            text = self.font_normal.render(option, True, color)
            self.screen.blit(text, rect)

        # Подсказка
        hint = self.hint_font.render(
            "МЫШЬ — выбор    ENTER — выбрать    ESC — продолжить",
            True,
            (150, 150, 150),
        )
        hint_rect = hint.get_rect(center=(sw // 2, sh - 50))
        self.screen.blit(hint, hint_rect)

        # ===== ОТРИСОВКА КАСТОМНОГО КУРСОРА (как в menu.py и character_selection.py) =====
        if self.cursor and self.cursor_hover:
            # Если мышь наведена на любой пункт меню, показываем курсор-hover, иначе обычный
            if mouse_over_any:
                self.screen.blit(self.cursor_hover, (mouse_pos[0], mouse_pos[1]))
            else:
                self.screen.blit(self.cursor, (mouse_pos[0], mouse_pos[1]))
        # ======================================================================
