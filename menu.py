import pygame
import os
from settings import *

# ================= ГЛАВНОЕ МЕНЮ =================
class Menu:
    def __init__(self, screen, game_settings):
        self.screen = screen
        self.settings = game_settings
        self.clock = pygame.time.Clock()
        self.running = True

        self.menu_items = ["Начать игру", "Загрузить", "Настройки", "Выход"]
        self.selected = 0

        # Загружаем шрифты
        base_path = os.path.join("assets", "fonts")
        title_font_path = os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf")
        if os.path.exists(title_font_path):
            self.title_font = pygame.font.Font(title_font_path, 84)
        else:
            self.title_font = pygame.font.Font(None, 84)

        button_font_path = os.path.join(base_path, "Philosopher-Bold.ttf")
        if os.path.exists(button_font_path):
            self.button_font = pygame.font.Font(button_font_path, 42)
        else:
            self.button_font = pygame.font.Font(None, 42)

        self.hint_font = pygame.font.Font(None, 24)

        # === Загрузка звуков ===
        self.sound_button = None      # push_button.wav - эффект нажатия
        self.music_loaded = False     # background_menu.wav - фоновая музыка

        try:
            # Инициализация микшера (если не был инициализирован глобально)
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            sounds_path = os.path.join("assets", "sounds", "menu")
            
            # 🔘 Звук кнопки (короткий эффект)
            button_path = os.path.join(sounds_path, "push_button.wav")
            if os.path.exists(button_path):
                self.sound_button = pygame.mixer.Sound(button_path)
                self.sound_button.set_volume(self.settings.master_volume * self.settings.music_volume)
                print(f"✓ Загружен звук кнопки: {button_path}")
            else:
                print(f"⚠ Звук кнопки не найден: {button_path}")
            
            # 🎵 Фоновая музыка (зацикленная)
            music_path = os.path.join(sounds_path, "background_menu.wav")
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.settings.master_volume * self.settings.music_volume)
                pygame.mixer.music.play(loops=-1)  # -1 = бесконечный цикл
                self.music_loaded = True
                print(f"✓ Запущена фоновая музыка: {music_path}")
            else:
                print(f"⚠ Фоновая музыка не найдена: {music_path}")
                
        except pygame.error as e:
            print(f"❌ Ошибка SDL_mixer: {e}")
        except Exception as e:
            print(f"❌ Ошибка загрузки звуков: {type(e).__name__}: {e}")

        # Загружаем видео (кадры будем масштабировать на лету)
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

    def _update_sound_volumes(self):
        """Применяет текущие настройки громкости к звукам"""
        vol = self.settings.master_volume * self.settings.music_volume
        if self.sound_button:
            self.sound_button.set_volume(vol)
        if self.music_loaded:
            pygame.mixer.music.set_volume(vol)

    def _play_button_sound(self):
        """Воспроизводит звук кнопки с проверкой"""
        if self.sound_button:
            try:
                self.sound_button.play()
            except pygame.error:
                pass  # Игнорируем ошибки воспроизведения

    def draw_button(self, text, x, y, width, height, is_selected):
        if is_selected:
            color = GOLD
            glow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*GOLD, 50), (0, 0, width + 10, height + 10), border_radius=12)
            self.screen.blit(glow_surface, (x - 5, y - 5))
        else:
            color = (150, 150, 150)

        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        button_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(button_surface, color, (0, 0, width, height), 3, border_radius=10)
        self.screen.blit(button_surface, (x, y))

        text_surface = self.button_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        while self.running:
            # Отрисовка видеофона
            if self.frames:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                frame = self.frames[self.current_frame]
                scaled_frame = pygame.transform.scale(frame, (screen_w, screen_h))
                self.screen.blit(scaled_frame, (0, 0))
            else:
                self.screen.fill(BLACK)

            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            title = self.title_font.render("", True, GOLD)
            title_rect = title.get_rect(center=(screen_w // 2, screen_h // 4))
            title_shadow = self.title_font.render("", True, (0, 0, 0))
            shadow_rect = title_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            self.screen.blit(title_shadow, shadow_rect)
            self.screen.blit(title, title_rect)

            subtitle = self.hint_font.render("", True, (180, 200, 150))
            subtitle_rect = subtitle.get_rect(center=(screen_w // 2, screen_h // 4 + 70))
            self.screen.blit(subtitle, subtitle_rect)

            button_w = 250
            button_h = 60
            start_x = screen_w // 2 - button_w // 2
            start_y = screen_h // 2 + 40

            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i in range(len(self.menu_items)):
                y = start_y + i * (button_h + 15)
                button_rect = pygame.Rect(start_x, y, button_w, button_h)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    if self.selected != i:
                        self.selected = i
                        self._play_button_sound()  # Звук при наведении

            for i, item in enumerate(self.menu_items):
                y = start_y + i * (button_h + 15)
                self.draw_button(item, start_x, y, button_w, button_h, i == self.selected)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        self._play_button_sound()  # Звук при подтверждении
                        return self.get_action()
                    elif event.key == pygame.K_ESCAPE:
                        return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i in range(len(self.menu_items)):
                            y = start_y + i * (button_h + 15)
                            button_rect = pygame.Rect(start_x, y, button_w, button_h)
                            if button_rect.collidepoint(event.pos):
                                self._play_button_sound()  # Звук при клике
                                return self.get_action(i)

            pygame.display.flip()
            self.clock.tick(30)

        return "exit"

    def get_action(self, index=None):
        if index is None:
            index = self.selected
        actions = {
            "Начать игру": "start",
            "Загрузить": "load",
            "Настройки": "settings",
            "Выход": "exit"
        }
        return actions.get(self.menu_items[index], "exit")


def show_menu(screen, game_settings):
    menu = Menu(screen, game_settings)
    return menu.run()


# ================= МЕНЮ НАСТРОЕК =================
class SettingsMenu:
    def __init__(self, screen, game_settings):
        self.screen = screen
        self.settings = game_settings
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_option = 0
        self.brightness_overlay = None

        # Шрифты
        base_path = os.path.join("assets", "fonts")
        title_font_path = os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf")
        if os.path.exists(title_font_path):
            self.title_font = pygame.font.Font(title_font_path, 60)
        else:
            self.title_font = pygame.font.Font(None, 60)

        button_font_path = os.path.join(base_path, "Philosopher-Bold.ttf")
        if os.path.exists(button_font_path):
            self.button_font = pygame.font.Font(button_font_path, 36)
            self.small_font = pygame.font.Font(button_font_path, 28)
        else:
            self.button_font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 28)

        # Видеофон
        self.video_frames = []
        video_path = os.path.join("assets", "videos", "settings_bg.mp4")
        try:
            import imageio
            if os.path.exists(video_path):
                print(f"Загрузка видео для настроек: {video_path}")
                video = imageio.get_reader(video_path)
                for i, frame in enumerate(video):
                    if i >= 300:
                        break
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.video_frames.append(frame_surface)
                self.current_video_frame = 0
                print(f"Загружено {len(self.video_frames)} кадров для настроек")
            else:
                print(f"Видео для настроек не найдено: {video_path}")
                self.video_frames = None
        except Exception as e:
            print(f"Ошибка загрузки видео для настроек: {e}")
            self.video_frames = None

        # Статичный фон как fallback
        self.background = None
        if not self.video_frames:
            bg_path = os.path.join("assets", "images", "menu", "settings_bg.jpg")
            if os.path.exists(bg_path):
                try:
                    self.background = pygame.image.load(bg_path).convert()
                except:
                    self.background = None

        self._build_menu_items()
        self.dragging = False
        self.drag_index = None
        self.toggle_rects = {}

    def _build_menu_items(self):
        res_options = self.settings.get_resolution_options()
        res_texts = [f"{w}x{h}" for w, h in res_options]
        current_res_index = self.settings.get_resolution_index()
        brightness = getattr(self.settings, 'brightness', 100)

        self.menu_items = [
            {"type": "slider", "label": "FPS", "min": 15, "max": 120, "value": self.settings.fps_limit, "step": 1},
            {"type": "choice", "label": "Разрешение", "options": res_texts, "value_index": current_res_index},
            {"type": "slider", "label": "Яркость", "min": 0, "max": 100, "value": brightness, "step": 1},
            {"type": "slider", "label": "Общий звук", "min": 0, "max": 100, "value": int(self.settings.master_volume * 100), "step": 1},
            {"type": "slider", "label": "Музыка", "min": 0, "max": 100, "value": int(self.settings.music_volume * 100), "step": 1},
            {"type": "toggle", "label": "Полный экран", "value": self.settings.fullscreen},
            {"type": "button", "label": "Назад", "action": "back"}
        ]

    def _update_sound_volumes(self):
        """Применяет настройки громкости ко всем звукам"""
        vol = self.settings.master_volume * self.settings.music_volume
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(vol)

    def update_value(self, index, new_value):
        item = self.menu_items[index]
        if item["type"] == "slider":
            item["value"] = new_value
            if item["label"] == "FPS":
                self.settings.fps_limit = new_value
            elif item["label"] == "Яркость":
                self.settings.brightness = new_value
                self.update_brightness()
            elif item["label"] == "Общий звук":
                self.settings.master_volume = new_value / 100.0
                self._update_sound_volumes()
            elif item["label"] == "Музыка":
                self.settings.music_volume = new_value / 100.0
                self._update_sound_volumes()
        elif item["type"] == "choice":
            item["value_index"] = new_value
            self.settings.set_resolution_by_index(new_value)
            self.screen = self.settings.apply_resolution(self.screen)
            self.update_brightness()
        elif item["type"] == "toggle":
            item["value"] = new_value
            self.settings.fullscreen = new_value
            self.screen = self.settings.apply_resolution(self.screen)
            self.update_brightness()

    def update_brightness(self):
        """Создаёт полупрозрачный оверлей для регулировки яркости"""
        if hasattr(self.settings, 'brightness'):
            brightness = self.settings.brightness
            alpha = int((100 - brightness) * 2.55)
            alpha = max(0, min(255, alpha))
            w = self.screen.get_width()
            h = self.screen.get_height()
            self.brightness_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            self.brightness_overlay.fill((0, 0, 0, alpha))
        else:
            self.brightness_overlay = None

    def draw_slider(self, x, y, width, value, min_val, max_val):
        bg_rect = pygame.Rect(x, y, width, 8)
        pygame.draw.rect(self.screen, (80, 80, 80), bg_rect, border_radius=4)
        t = (value - min_val) / (max_val - min_val)
        fill_width = int(width * t)
        fill_rect = pygame.Rect(x, y, fill_width, 8)
        pygame.draw.rect(self.screen, GOLD, fill_rect, border_radius=4)
        handle_x = x + fill_width
        pygame.draw.circle(self.screen, GOLD, (handle_x, y + 4), 10)
        return handle_x

    def draw_button(self, text, x, y, width, height, is_selected):
        color = GOLD if is_selected else (150, 150, 150)
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        button_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(button_surface, color, (0, 0, width, height), 3, border_radius=10)
        self.screen.blit(button_surface, (x, y))
        text_surface = self.button_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        
        if not hasattr(self.settings, 'brightness'):
            self.settings.brightness = 100
        self.update_brightness()

        # Отрисовка фона
        if self.video_frames:
            self.current_video_frame = (self.current_video_frame + 1) % len(self.video_frames)
            frame = self.video_frames[self.current_video_frame]
            scaled_frame = pygame.transform.scale(frame, (screen_w, screen_h))
            self.screen.blit(scaled_frame, (0, 0))
        elif self.background:
            bg_scaled = pygame.transform.scale(self.background, (screen_w, screen_h))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            self.screen.fill(BLACK)
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

        if self.brightness_overlay:
            self.screen.blit(self.brightness_overlay, (0, 0))

        # Заголовок
        title = self.title_font.render("НАСТРОЙКИ", True, GOLD)
        title_rect = title.get_rect(center=(screen_w // 2, 80))
        self.screen.blit(title, title_rect)

        start_x = screen_w // 2 - 300
        item_height = 70
        start_y = 180

        # Отрисовка элементов
        for i, item in enumerate(self.menu_items):
            y = start_y + i * item_height
            label_surf = self.small_font.render(item["label"], True, WHITE)
            self.screen.blit(label_surf, (start_x, y))

            if item["type"] == "slider":
                value_str = str(item["value"])
                value_surf = self.small_font.render(value_str, True, GOLD)
                self.screen.blit(value_surf, (start_x + 250, y))
                slider_x = start_x + 320
                slider_width = 200
                self.draw_slider(slider_x, y + 15, slider_width, item["value"], item["min"], item["max"])

            elif item["type"] == "choice":
                current_option = item["options"][item["value_index"]]
                choice_surf = self.small_font.render(current_option, True, GOLD)
                self.screen.blit(choice_surf, (start_x + 250, y))
                left_arrow = self.small_font.render("<", True, GOLD if i == self.selected_option else (150, 150, 150))
                right_arrow = self.small_font.render(">", True, GOLD if i == self.selected_option else (150, 150, 150))
                self.screen.blit(left_arrow, (start_x + 220, y))
                self.screen.blit(right_arrow, (start_x + 380, y))

            elif item["type"] == "toggle":
                state = "ON" if item["value"] else "OFF"
                toggle_surf = self.small_font.render(state, True, GOLD if item["value"] else RED)
                toggle_rect = toggle_surf.get_rect(topleft=(start_x + 250, y))
                self.toggle_rects[i] = toggle_rect
                self.screen.blit(toggle_surf, (start_x + 250, y))

            elif item["type"] == "button":
                btn_w, btn_h = 200, 50
                btn_x = screen_w // 2 - btn_w // 2
                btn_y = y + 10
                self.draw_button(item["label"], btn_x, btn_y, btn_w, btn_h, i == self.selected_option)

        # Обработка событий
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.settings.save()
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_items)
                    self.dragging = False
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_items)
                    self.dragging = False
                elif event.key == pygame.K_LEFT:
                    self._change_value(-1)
                elif event.key == pygame.K_RIGHT:
                    self._change_value(1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    if self.menu_items[self.selected_option]["type"] == "button":
                        self.settings.save()
                        return "back"
                    else:
                        if self.menu_items[self.selected_option]["type"] == "toggle":
                            new_val = not self.menu_items[self.selected_option]["value"]
                            self.update_value(self.selected_option, new_val)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Ползунки
                    for i, item in enumerate(self.menu_items):
                        if item["type"] == "slider":
                            y = start_y + i * item_height
                            slider_x = start_x + 320
                            slider_width = 200
                            if slider_x <= mouse_x <= slider_x + slider_width and y + 10 <= mouse_y <= y + 30:
                                self.dragging = True
                                self.drag_index = i
                                self._set_slider_from_mouse(i, mouse_x, slider_x, slider_width)
                                break
                    # Стрелки выбора
                    for i, item in enumerate(self.menu_items):
                        if item["type"] == "choice":
                            y = start_y + i * item_height
                            if start_x + 210 <= mouse_x <= start_x + 230 and y <= mouse_y <= y + 30:
                                self._change_value(-1, i)
                            elif start_x + 370 <= mouse_x <= start_x + 390 and y <= mouse_y <= y + 30:
                                self._change_value(1, i)
                    # Тоггл
                    for i, item in enumerate(self.menu_items):
                        if item["type"] == "toggle" and i in self.toggle_rects:
                            if self.toggle_rects[i].collidepoint(mouse_x, mouse_y):
                                new_val = not item["value"]
                                self.update_value(i, new_val)
                                break
                    # Кнопка "Назад"
                    for i, item in enumerate(self.menu_items):
                        if item["type"] == "button":
                            btn_w, btn_h = 200, 50
                            btn_x = screen_w // 2 - btn_w // 2
                            btn_y = start_y + i * item_height + 10
                            if btn_x <= mouse_x <= btn_x + btn_w and btn_y <= mouse_y <= btn_y + btn_h:
                                self.settings.save()
                                return "back"
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    i = self.drag_index
                    item = self.menu_items[i]
                    if item["type"] == "slider":
                        slider_x = start_x + 320
                        slider_width = 200
                        self._set_slider_from_mouse(i, mouse_x, slider_x, slider_width)

        pygame.display.flip()
        self.clock.tick(30)
        return None

    def _set_slider_from_mouse(self, index, mouse_x, slider_x, slider_width):
        item = self.menu_items[index]
        t = (mouse_x - slider_x) / slider_width
        t = max(0, min(1, t))
        new_val = item["min"] + int(t * (item["max"] - item["min"] + 0.5))
        new_val = max(item["min"], min(item["max"], new_val))
        if new_val != item["value"]:
            self.update_value(index, new_val)

    def _change_value(self, delta, index=None):
        if index is None:
            index = self.selected_option
        item = self.menu_items[index]
        if item["type"] == "slider":
            new_val = item["value"] + delta * item["step"]
            new_val = max(item["min"], min(item["max"], new_val))
            self.update_value(index, new_val)
        elif item["type"] == "choice":
            new_idx = item["value_index"] + delta
            if 0 <= new_idx < len(item["options"]):
                self.update_value(index, new_idx)
        elif item["type"] == "toggle":
            if delta != 0:
                new_val = not item["value"]
                self.update_value(index, new_val)


def show_settings(screen, game_settings):
    settings_menu = SettingsMenu(screen, game_settings)
    while True:
        result = settings_menu.run()
        if result in ("back", "exit"):
            return result
