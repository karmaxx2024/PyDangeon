import os
import json
import pygame
import shutil
from datetime import datetime
from settings import *

# ============================================================
#                      МЕНЮ ЗАГРУЗКИ / СОХРАНЕНИЯ
# ============================================================

class LoadSaveMenu:
    """Меню управления сохранениями (как в Minecraft)"""
    def __init__(self, screen, game_settings):
        self.screen = screen
        self.settings = game_settings
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_index = 0
        self.scroll_offset = 0

        # Папка с сохранениями
        self.saves_dir = "saves"
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

        # Список файлов
        self.save_files = []
        self.refresh_save_list()

        # Состояние: "browse" (обычный), "new_save" (ввод имени)
        self.mode = "browse"
        self.input_text = ""
        self.input_active = True
        self.input_error = ""

        # Загрузка шрифтов (как в других меню)
        base_path = os.path.join("assets", "fonts")
        title_path = os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf")
        if os.path.exists(title_path):
            self.title_font = pygame.font.Font(title_path, 64)
        else:
            self.title_font = pygame.font.Font(None, 64)

        btn_path = os.path.join(base_path, "Philosopher-Bold.ttf")
        if os.path.exists(btn_path):
            self.button_font = pygame.font.Font(btn_path, 36)
            self.small_font = pygame.font.Font(btn_path, 26)
            self.hint_font = pygame.font.Font(btn_path, 22)
        else:
            self.button_font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 26)
            self.hint_font = pygame.font.Font(None, 22)

        # Курсор (как в menu.py)
        try:
            self.cursor_hover = pygame.image.load("assets/images/menu/mouse2.png").convert_alpha()
            self.cursor_hover = pygame.transform.smoothscale(self.cursor_hover, (64, 64))
            self.cursor = pygame.image.load("assets/images/menu/mouse1.png").convert_alpha()
            self.cursor = pygame.transform.smoothscale(self.cursor, (64, 64))
        except:
            self.cursor = None
            self.cursor_hover = None
        pygame.mouse.set_visible(False)

        # Видеофон
        self.frames = []
        video_path = os.path.join("assets", "videos", "menu_bg.mp4")
        try:
            import imageio
            if os.path.exists(video_path):
                video = imageio.get_reader(video_path)
                for i, frame in enumerate(video):
                    if i >= 300:
                        break
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.frames.append(frame_surface)
                self.current_frame = 0
        except:
            pass

        # Кнопки
        self.button_rects = {}

    # ---------- РАБОТА С ФАЙЛАМИ ----------
    def refresh_save_list(self):
        """Обновляет список сохранений (сортировка по дате)"""
        files = []
        for f in os.listdir(self.saves_dir):
            if f.endswith(".json"):
                path = os.path.join(self.saves_dir, f)
                mtime = os.path.getmtime(path)
                files.append({
                    "name": f.replace(".json", ""),
                    "path": path,
                    "date": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                })
        files.sort(key=lambda x: x["date"], reverse=True)
        self.save_files = files
        # Сброс выбора, если вышли за пределы
        if self.selected_index >= len(self.save_files):
            self.selected_index = max(0, len(self.save_files) - 1)

    def get_save_data(self, filename):
        """Загружает данные из файла сохранения"""
        path = os.path.join(self.saves_dir, filename + ".json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete_save(self, filename):
        """Удаляет файл сохранения"""
        path = os.path.join(self.saves_dir, filename + ".json")
        if os.path.exists(path):
            os.remove(path)
            self.refresh_save_list()
            return True
        return False

    def save_game_data(self, filename, data):
        """Сохраняет данные в файл"""
        path = os.path.join(self.saves_dir, filename + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.refresh_save_list()

    # ---------- ОТРИСОВКА ----------
    def draw_background(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        if self.frames:
            frame = self.frames[self.current_frame]
            frame = pygame.transform.scale(frame, (sw, sh))
            self.screen.blit(frame, (0, 0))
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        else:
            self.screen.fill((15, 15, 25))

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60))
        self.screen.blit(overlay, (0, 0))

    def draw_list(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        self.button_rects.clear()

        # Заголовок
        title = self.title_font.render("УПРАВЛЕНИЕ МИРАМИ", True, GOLD)
        title_rect = title.get_rect(center=(sw//2, 70))
        self.screen.blit(title, title_rect)

        # Подзаголовок
        if self.mode == "browse":
            sub = self.hint_font.render("Выберите мир для загрузки или создайте новый", True, (200,200,200))
        else:
            sub = self.hint_font.render("Введите имя нового мира (ENTER - сохранить, ESC - отмена)", True, (200,200,200))
        sub_rect = sub.get_rect(center=(sw//2, 120))
        self.screen.blit(sub, sub_rect)

        # Область списка
        list_x = sw // 2 - 300
        list_y = 160
        list_w = 600
        list_h = sh - 300
        item_h = 60
        max_visible = list_h // item_h

        # Фон списка
        pygame.draw.rect(self.screen, (0,0,0,150), (list_x, list_y, list_w, list_h), border_radius=10)
        pygame.draw.rect(self.screen, (100,100,100), (list_x, list_y, list_w, list_h), 2, border_radius=10)

        # Прокрутка
        total_items = len(self.save_files)
        if total_items > max_visible:
            scroll_max = total_items - max_visible
            scroll_ratio = self.scroll_offset / scroll_max if scroll_max > 0 else 0
            scroll_bar_w = 8
            scroll_bar_h = max(30, list_h * (max_visible / total_items))
            scroll_bar_x = list_x + list_w - 20
            scroll_bar_y = list_y + (list_h - scroll_bar_h) * scroll_ratio
            pygame.draw.rect(self.screen, (80,80,80), (scroll_bar_x, list_y, scroll_bar_w, list_h), border_radius=4)
            pygame.draw.rect(self.screen, (200,200,200), (scroll_bar_x, scroll_bar_y, scroll_bar_w, scroll_bar_h), border_radius=4)

        # Элементы списка
        start_idx = self.scroll_offset
        end_idx = min(start_idx + max_visible, total_items)

        for i in range(start_idx, end_idx):
            save = self.save_files[i]
            y = list_y + 10 + (i - start_idx) * item_h
            rect = pygame.Rect(list_x + 10, y, list_w - 30, item_h - 4)

            # Подсветка выбранного
            is_selected = (i == self.selected_index)
            color = (60,60,80) if is_selected else (30,30,40)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            if is_selected:
                pygame.draw.rect(self.screen, GOLD, rect, 2, border_radius=6)

            # Имя и дата
            name_surf = self.button_font.render(save["name"], True, WHITE)
            self.screen.blit(name_surf, (rect.x + 10, rect.y + 4))
            date_surf = self.small_font.render(save["date"], True, (150,150,150))
            self.screen.blit(date_surf, (rect.x + 10, rect.y + 30))

            # Кнопка удаления (крестик) для выбранного
            if is_selected and self.mode == "browse":
                del_x = rect.right - 40
                del_y = rect.y + 4
                del_rect = pygame.Rect(del_x, del_y, 32, 32)
                self.button_rects[f"del_{i}"] = del_rect
                pygame.draw.circle(self.screen, (200,50,50), del_rect.center, 14)
                cross = self.hint_font.render("✕", True, WHITE)
                cross_rect = cross.get_rect(center=del_rect.center)
                self.screen.blit(cross, cross_rect)

        # Кнопки управления (внизу)
        btn_w = 160
        btn_h = 50
        btn_y = sh - 90

        if self.mode == "browse":
            btns = [
                ("ЗАГРУЗИТЬ", "load"),
                ("СОЗДАТЬ", "new"),
                ("НАЗАД", "back")
            ]
        else:
            btns = [
                ("СОХРАНИТЬ", "save_new"),
                ("ОТМЕНА", "cancel")
            ]

        for idx, (label, action) in enumerate(btns):
            x = sw//2 - (len(btns)*btn_w + (len(btns)-1)*20)//2 + idx*(btn_w+20)
            rect = pygame.Rect(x, btn_y, btn_w, btn_h)
            self.button_rects[action] = rect

            # Цвет
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            color = GOLD if is_hover else (100,100,100)
            bg = (40,40,50) if is_hover else (20,20,30)
            pygame.draw.rect(self.screen, bg, rect, border_radius=8)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=8)
            text = self.button_font.render(label, True, color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Если режим ввода имени
        if self.mode == "new_save":
            input_rect = pygame.Rect(sw//2 - 200, sh//2 - 40, 400, 60)
            pygame.draw.rect(self.screen, (40,40,50), input_rect, border_radius=8)
            pygame.draw.rect(self.screen, GOLD, input_rect, 3, border_radius=8)
            name_surf = self.button_font.render(self.input_text + ("|" if self.input_active else ""), True, WHITE)
            name_rect = name_surf.get_rect(center=input_rect.center)
            self.screen.blit(name_surf, name_rect)

            if self.input_error:
                err_surf = self.hint_font.render(self.input_error, True, RED)
                err_rect = err_surf.get_rect(center=(sw//2, sh//2 + 70))
                self.screen.blit(err_surf, err_rect)

    def draw(self):
        self.draw_background()
        self.draw_list()

        # Курсор
        mx, my = pygame.mouse.get_pos()
        if self.cursor and self.cursor_hover:
            hover = False
            for rect in self.button_rects.values():
                if rect.collidepoint(mx, my):
                    hover = True
                    break
            # Также проверяем элементы списка
            if not hover:
                list_x = self.screen.get_width()//2 - 300
                list_y = 160
                list_w = 600
                list_h = self.screen.get_height() - 300
                if list_x <= mx <= list_x+list_w and list_y <= my <= list_y+list_h:
                    # Проверим каждый элемент списка
                    item_h = 60
                    idx = (my - list_y - 10) // item_h + self.scroll_offset
                    if 0 <= idx < len(self.save_files):
                        hover = True

            if hover:
                self.screen.blit(self.cursor_hover, (mx, my))
            else:
                self.screen.blit(self.cursor, (mx, my))

        pygame.display.flip()

    # ---------- ОБРАБОТКА ВВОДА ----------
    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if self.mode == "browse":
                    if event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.save_files)-1, self.selected_index + 1)
                    elif event.key == pygame.K_RETURN:
                        return self.action_load()
                    elif event.key == pygame.K_ESCAPE:
                        return "back"
                    elif event.key == pygame.K_DELETE:
                        if self.save_files:
                            self.delete_save(self.save_files[self.selected_index]["name"])
                else:  # new_save
                    if event.key == pygame.K_ESCAPE:
                        self.mode = "browse"
                        self.input_text = ""
                        self.input_error = ""
                    elif event.key == pygame.K_RETURN:
                        return self.action_save_new()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if event.unicode.isprintable() and len(self.input_text) < 30:
                            self.input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Проверяем клик по списку
                    list_x = self.screen.get_width()//2 - 300
                    list_y = 160
                    list_w = 600
                    list_h = self.screen.get_height() - 300
                    if list_x <= mx <= list_x+list_w and list_y <= my <= list_y+list_h:
                        item_h = 60
                        idx = (my - list_y - 10) // item_h + self.scroll_offset
                        if 0 <= idx < len(self.save_files):
                            self.selected_index = idx
                            # Если клик по крестику удаления
                            if self.mode == "browse":
                                del_key = f"del_{idx}"
                                if del_key in self.button_rects and self.button_rects[del_key].collidepoint(mx, my):
                                    self.delete_save(self.save_files[idx]["name"])
                                    return None

                    # Проверяем кнопки
                    for action, rect in self.button_rects.items():
                        if rect.collidepoint(mx, my):
                            if action == "load":
                                return self.action_load()
                            elif action == "new":
                                self.mode = "new_save"
                                self.input_text = ""
                                self.input_error = ""
                                return None
                            elif action == "back":
                                return "back"
                            elif action == "save_new":
                                return self.action_save_new()
                            elif action == "cancel":
                                self.mode = "browse"
                                self.input_text = ""
                                self.input_error = ""
                                return None
        return None

    def action_load(self):
        if not self.save_files:
            return None
        filename = self.save_files[self.selected_index]["name"]
        return f"load:{filename}"

    def action_save_new(self):
        name = self.input_text.strip()
        if not name:
            self.input_error = "Имя не может быть пустым"
            return None
        # Проверка на существование
        if os.path.exists(os.path.join(self.saves_dir, name + ".json")):
            self.input_error = "Мир с таким именем уже существует"
            return None
        # Возвращаем команду на создание нового сохранения
        return f"save_new:{name}"

    # ---------- ЗАПУСК ----------
    def run(self):
        while self.running:
            result = self.handle_events()
            if result:
                return result
            self.draw()
            self.clock.tick(60)
        return "back"

# ============================================================
#          ФУНКЦИИ СЕРИАЛИЗАЦИИ / ДЕСЕРИАЛИЗАЦИИ
# ============================================================

def serialize_game(player, dungeon, doors, visited=None):
    """Собирает все данные игры в словарь для сохранения"""
    data = {
        "player": {
            "x": player.x,
            "y": player.y,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "attack": player.attack,
            "speed": player.speed,
            "name": player.name,
            "color": player.color,
            "image": getattr(player, 'image_path', None)  # если сохранять путь
        },
        "maze": dungeon.maze_gen.maze,  # двумерный массив bool
        "width": dungeon.width,
        "height": dungeon.height,
        "doors": [],
        "visited": visited if visited else None  # можно не сохранять
    }
    # Сохраняем двери
    for door in doors:
        data["doors"].append({
            "x": door.x,
            "y": door.y,
            "width": door.width,
            "height": door.height,
            "is_open": door.is_open
        })
    return data

def deserialize_game(data):
    """Восстанавливает игровые объекты из данных"""
    # Восстановим dungeon
    from world_map import DungeonGenerator
    dungeon = DungeonGenerator(data["width"], data["height"])
    # Вместо генерации загружаем maze
    dungeon.maze_gen.maze = data["maze"]
    dungeon._build_collision_from_maze()
    # Восстанавливаем двери
    from objects import Door
    doors = []
    for d in data["doors"]:
        door = Door(d["x"], d["y"], d["width"], d["height"], d["is_open"])
        doors.append(door)
    # Восстанавливаем игрока
    from player import Player
    # Для создания игрока нужны char_data, но у нас есть все параметры
    char_data = {
        "name": data["player"]["name"],
        "hp": data["player"]["max_hp"],
        "attack": data["player"]["attack"],
        "speed": data["player"]["speed"],
        "color": data["player"]["color"],
        "image": data["player"].get("image")
    }
    player = Player(data["player"]["x"], data["player"]["y"], char_data)
    player.hp = data["player"]["hp"]
    # Восстанавливаем visited, если есть
    visited = data.get("visited")
    if visited:
        dungeon.visited = visited
    else:
        # Сбрасываем туман (все тайлы непосещены)
        dungeon.visited = [[False] * dungeon.width for _ in range(dungeon.height)]
    return player, dungeon, doors