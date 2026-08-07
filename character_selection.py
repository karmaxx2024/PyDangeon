import os
import pygame
from settings import *
from player import _load_sprite

_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images", "player")
KNIGHT_IMAGE = os.path.join(_ASSETS, "knight.jpg")
MAG_IMAGE = os.path.join(_ASSETS, "mag.jpg")
ROGUE_IMAGE = os.path.join(_ASSETS, "razboynik.jpg")

CHARACTERS = [
    {
        "name": "Рыцарь",
        "description": "Крепкий и сильный. Медленный, но не умирает.",
        "hp": 120,
        "attack": 15,
        "speed": 3,
        "color": (200, 60, 60),
        "image": KNIGHT_IMAGE,
    },
    {
        "name": "Маг",
        "description": "Слабый физически, но магия очень мощная.",
        "hp": 60,
        "attack": 30,
        "speed": 4,
        "image": MAG_IMAGE,
        "mana": 100,
        "color": (80, 80, 220),
    },
    {
        "name": "Разбойник",
        "description": "Быстрый и ловкий. Средние характеристики.",
        "hp": 80,
        "attack": 20,
        "speed": 6,
        "image": ROGUE_IMAGE,
        "color": (60, 180, 60),
    },
]

class CharacterSelect:
    def __init__(self, screen, game_settings):
        self.screen = screen
        self.settings = game_settings
        self.clock = pygame.time.Clock()
        self.selected = 0

        base_path = os.path.join("assets", "fonts")

        title_path = os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf")
        if os.path.exists(title_path):
            self.title_font = pygame.font.Font(title_path, 64)
        else:
            self.title_font = pygame.font.Font(None, 64)

        btn_path = os.path.join(base_path, "Philosopher-Bold.ttf")
        if os.path.exists(btn_path):
            self.name_font = pygame.font.Font(btn_path, 38)
            self.stat_font = pygame.font.Font(btn_path, 24)
            self.hint_font = pygame.font.Font(btn_path, 20)
        else:
            self.name_font = pygame.font.Font(None, 38)
            self.stat_font = pygame.font.Font(None, 24)
            self.hint_font = pygame.font.Font(None, 20)

        self.frames = []
        video_path = os.path.join("assets", "videos", "menu_bg.mp4")
        try:
            import imageio
            if os.path.exists(video_path):
                print(f"Загрузка видео: {video_path}")
                video = imageio.get_reader(video_path)
                for i, frame in enumerate(video):
                    if i >= 300:
                        break
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.frames.append(frame_surface)
                self.current_frame = 0
                print(f"Загружено {len(self.frames)} кадров")
            else:
                print(f"Видео не найдено: {video_path}")
        except Exception as e:
            print(f"Ошибка видео: {e}")

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines

    def _draw_stat_bar(self, x, y, label, value, max_value, color, bar_w):
        label_surf = self.stat_font.render(label, True, WHITE)
        self.screen.blit(label_surf, (x, y))

        bar_x = x + 105
        bar_h = 12

        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, y + 5, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * value / max_value)
        pygame.draw.rect(self.screen, color, (bar_x, y + 5, fill_w, bar_h), border_radius=5)

        val_surf = self.stat_font.render(str(value), True, GOLD)
        self.screen.blit(val_surf, (bar_x + bar_w + 8, y))

    def _draw_card(self, char, cx, cy, card_w, card_h, is_selected):
        border_color = GOLD if is_selected else (80, 80, 80)
        alpha = 220 if is_selected else 140
        radius = 20  # увеличенный радиус скругления

        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)

        # Заливка фона со скруглёнными углами
        pygame.draw.rect(card, (20, 20, 20, alpha), (0, 0, card_w, card_h), border_radius=radius)

        # Рамка со скруглёнными углами
        pygame.draw.rect(card, border_color, (0, 0, card_w, card_h), 3, border_radius=radius)

        self.screen.blit(card, (cx, cy))

        avatar_cx = cx + card_w // 2
        avatar_cy = cy + 75
        avatar_r = 100

        image_path = char.get("image")
        sprite = _load_sprite(image_path, avatar_r * 2)
        if sprite:
            sprite_rect = sprite.get_rect(center=(avatar_cx, avatar_cy))
            self.screen.blit(sprite, sprite_rect)
        else:
            pygame.draw.circle(self.screen, (40, 40, 40), (avatar_cx + 3, avatar_cy + 3), avatar_r + 2)
            pygame.draw.circle(self.screen, char["color"], (avatar_cx, avatar_cy), avatar_r)
            pygame.draw.circle(self.screen, WHITE, (avatar_cx, avatar_cy), avatar_r, 2)

            first_letter = char["name"][0]
            letter_surf = self.name_font.render(first_letter, True, WHITE)
            letter_rect = letter_surf.get_rect(center=(avatar_cx, avatar_cy))
            self.screen.blit(letter_surf, letter_rect)

        name_surf = self.name_font.render(char["name"], True, GOLD if is_selected else WHITE)
        name_rect = name_surf.get_rect(centerx=cx + card_w // 2, top=cy + 130)
        self.screen.blit(name_surf, name_rect)

        padding = 16
        desc_lines = self._wrap_text(char["description"], self.hint_font, card_w - padding * 2)
        for j, line in enumerate(desc_lines):
            line_surf = self.hint_font.render(line, True, (180, 180, 180))
            line_rect = line_surf.get_rect(centerx=cx + card_w // 2, top=cy + 178 + j * 22)
            self.screen.blit(line_surf, line_rect)

        bar_w = card_w - 95 - 14 - 14 - 40
        stat_x = cx + 14
        self._draw_stat_bar(stat_x, cy + 235, "HP", char["hp"], 120, (220, 60, 60), bar_w)
        self._draw_stat_bar(stat_x, cy + 268, "Атака", char["attack"], 30, (220, 160, 40), bar_w)
        self._draw_stat_bar(stat_x, cy + 301, "Скорость", char["speed"], 6, (60, 180, 220), bar_w)

        if is_selected:
            hint = self.hint_font.render("[ Enter / Клик — выбрать ]", True, GOLD)
            hint_rect = hint.get_rect(centerx=cx + card_w // 2, top=cy + card_h - 34)
            self.screen.blit(hint, hint_rect)

    def run(self):
        sw = self.screen.get_width()
        sh = self.screen.get_height()

        card_w = 320
        card_h = 420
        gap = 40
        total_w = len(CHARACTERS) * card_w + (len(CHARACTERS) - 1) * gap
        start_x = sw // 2 - total_w // 2
        cards_y = sh // 2 - card_h // 2 + 20

        while True:
            if self.frames:
                frame = self.frames[self.current_frame]
                frame = pygame.transform.scale(frame, (sw, sh))
                self.screen.blit(frame, (0, 0))
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            else:
                self.screen.fill((15, 15, 25))

            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for i in range(sh):
                alpha = int(60 * i / sh)
                pygame.draw.line(overlay, (30, 10, 60, alpha), (0, i), (sw, i))
            self.screen.blit(overlay, (0, 0))

            title_surf = self.title_font.render("ВЫБОР ПЕРСОНАЖА", True, GOLD)
            title_rect = title_surf.get_rect(centerx=sw // 2, top=30)
            self.screen.blit(title_surf, title_rect)

            mouse_x, mouse_y = pygame.mouse.get_pos()

            for i, char in enumerate(CHARACTERS):
                cx = start_x + i * (card_w + gap)
                card_rect = pygame.Rect(cx, cards_y, card_w, card_h)
                if card_rect.collidepoint(mouse_x, mouse_y):
                    self.selected = i
                self._draw_card(char, cx, cards_y, card_w, card_h, i == self.selected)

            arrow_left = self.name_font.render("<", True, GOLD if self.selected > 0 else (60, 60, 60))
            arrow_right = self.name_font.render(">", True, GOLD if self.selected < len(CHARACTERS) - 1 else (60, 60, 60))
            self.screen.blit(arrow_left, (start_x - 50, cards_y + card_h // 2 - 20))
            self.screen.blit(arrow_right, (start_x + total_w + 16, cards_y + card_h // 2 - 20))

            # Кнопка "НАЗАД" с полностью скруглёнными углами (капсула)
            btn_w, btn_h = 240, 60
            btn_x = sw // 2 - btn_w // 2
            btn_y = cards_y + card_h + 18

            back_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            hovered = back_button_rect.collidepoint(mouse_x, mouse_y)

            button_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)

            bg_color = (20, 20, 25, 180) if not hovered else (30, 30, 35, 220)
            border_color = GOLD if hovered else (120, 120, 120)
            btn_radius = 30  # половина высоты для идеальной капсулы

            # Заливка фона со скруглением
            pygame.draw.rect(button_surf, bg_color, (0, 0, btn_w, btn_h), border_radius=btn_radius)
            # Рамка со скруглением
            pygame.draw.rect(button_surf, border_color, (0, 0, btn_w, btn_h), 3, border_radius=btn_radius)

            text_color = WHITE if hovered else (180, 180, 180)
            back_text = self.name_font.render(" < НАЗАД", True, text_color)
            text_rect = back_text.get_rect(center=(btn_w // 2, btn_h // 2))
            button_surf.blit(back_text, text_rect)

            self.screen.blit(button_surf, (btn_x, btn_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.selected = max(0, self.selected - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.selected = min(len(CHARACTERS) - 1, self.selected + 1)
                    elif event.key == pygame.K_RETURN:
                        return dict(CHARACTERS[self.selected])
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i in range(len(CHARACTERS)):
                        cx = start_x + i * (card_w + gap)
                        card_rect = pygame.Rect(cx, cards_y, card_w, card_h)
                        if card_rect.collidepoint(event.pos):
                            if self.selected == i:
                                return dict(CHARACTERS[self.selected])
                            self.selected = i
                    if back_button_rect.collidepoint(event.pos):
                        return None

            pygame.display.flip()
            self.clock.tick(60)


def show_character_select(screen, game_settings):
    cs = CharacterSelect(screen, game_settings)
    return cs.run()
