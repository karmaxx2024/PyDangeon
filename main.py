import pygame
import sys
import os
import json
from settings import *
from menu import show_menu, show_settings
from settings import GameSettings
from character_selection import show_character_select
from player import Player
from tilemap import load_floor_tile, load_wall_tile, draw_floor_with_camera, generate_floor_layout, FLOOR_IMAGE, \
    FLOOR_MOSS_IMAGE
from world_map import DungeonGenerator, update_camera, calc_camera_viewport, scale_surface, FOG_RADIUS_TILES
from objects import Door
from pause_menu import PauseMenu
from load_save_menu import LoadSaveMenu, serialize_game, deserialize_game

# ============================================================
#                   ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
# ============================================================

def game_loop(screen, settings, char_data=None, loaded_player=None, loaded_dungeon=None, loaded_doors=None):
    """
    Запускает игру.
    Если переданы loaded_player, loaded_dungeon, loaded_doors — загружает сохранённое состояние.
    Иначе генерирует новое подземелье с выбранным персонажем.
    """
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    hint_font = pygame.font.Font(None, 24)

    pygame.mouse.set_visible(False)

    sw = screen.get_width()
    sh = screen.get_height()

    # ---------- ЗАГРУЗКА СОХРАНЕНИЯ ИЛИ НОВАЯ ИГРА ----------
    if loaded_player is not None and loaded_dungeon is not None and loaded_doors is not None:
        # Используем загруженные объекты
        player = loaded_player
        dungeon = loaded_dungeon
        doors = loaded_doors
        # Загружаем текстуры заново (они не сохраняются)
        floor_tile = load_floor_tile(FLOOR_IMAGE)
        floor_moss_tile = load_floor_tile(FLOOR_MOSS_IMAGE)
        wall_tile = load_wall_tile()
        # Создаём группу объектов для дверей
        objects_group = pygame.sprite.Group()
        for door in doors:
            objects_group.add(door)
        # Получаем размер карты
        map_width_px, map_height_px = dungeon.get_map_size_pixels()
        floor_layout = generate_floor_layout(map_width_px, map_height_px, TILE_SIZE, moss_chance=0.20)
        # Проверка стены
        wall_texture_ok = wall_tile is not None
        if not wall_texture_ok:
            wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_tile.fill((100, 100, 100))
        # Подсчёт факелов (для отладки)
        torch_positions = dungeon.get_torch_positions()
        print("=== ЗАГРУЖЕНО СОХРАНЕНИЕ ===")
        print(f"Стен: {len(dungeon.collision_rects)}")
        print(f"Дверей: {len(doors)}")
    else:
        # Новая игра — генерируем
        if char_data is None:
            # Если вдруг не передан персонаж — берём первого из списка
            from character_selection import CHARACTERS
            char_data = dict(CHARACTERS[0])
        dungeon = DungeonGenerator(MAP_WIDTH, MAP_HEIGHT)
        map_width_px, map_height_px = dungeon.get_map_size_pixels()
        start_x, start_y = dungeon.get_player_start_position()
        player = Player(start_x, start_y, char_data)

        floor_tile = load_floor_tile(FLOOR_IMAGE)
        floor_moss_tile = load_floor_tile(FLOOR_MOSS_IMAGE)
        floor_layout = generate_floor_layout(map_width_px, map_height_px, TILE_SIZE, moss_chance=0.20)
        wall_tile = load_wall_tile()
        wall_texture_ok = wall_tile is not None
        if not wall_texture_ok:
            wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_tile.fill((100, 100, 100))

        # Двери
        objects_group = pygame.sprite.Group()
        door_positions = dungeon.get_door_positions()
        doors = []
        for door_data in door_positions:
            x, y, width, height = door_data
            door = Door(x, y, width, height, is_open=False)
            objects_group.add(door)
            doors.append(door)

        torch_positions = dungeon.get_torch_positions()
        # (факелы закомментированы в оригинале)
        print("=== НОВЫЙ ЛАБИРИНТ СОЗДАН ===")
        print(f"Стен: {len(dungeon.collision_rects)}")
        print(f"Дверей: {len(doors)}")

    # ---------- ОБЩАЯ НАСТРОЙКА ----------
    camera_x = 0
    camera_y = 0
    zoom, view_w, view_h = calc_camera_viewport(sw, sh)

    def refresh_scaled_tiles():
        return (
            scale_surface(floor_tile, zoom),
            scale_surface(floor_moss_tile, zoom) if floor_moss_tile else None,
            scale_surface(wall_tile, zoom),
        )

    scaled_floor, scaled_moss, scaled_wall = refresh_scaled_tiles()

    def draw_object(obj):
        sx = (obj.rect.x - camera_x) * zoom
        sy = (obj.rect.y - camera_y) * zoom
        if zoom != 1.0:
            w = max(1, int(obj.rect.width * zoom))
            h = max(1, int(obj.rect.height * zoom))
            screen.blit(pygame.transform.scale(obj.image, (w, h)), (sx, sy))
        else:
            screen.blit(obj.image, (sx, sy))

    def draw_scene():
        screen.fill((20, 20, 30))
        draw_floor_with_camera(screen, scaled_floor, scaled_moss, floor_layout, camera_x, camera_y, zoom)
        dungeon.draw(screen, camera_x, camera_y, scaled_wall, zoom)
        for obj in objects_group:
            draw_object(obj)
        player.draw_with_camera(screen, camera_x, camera_y, zoom)
        dungeon.draw_fog(screen, player, camera_x, camera_y, zoom, debug_mode)

    debug_mode = False
    pause_menu = PauseMenu(screen)

    # ---------- ФУНКЦИЯ СОХРАНЕНИЯ ----------
    def quick_save(filename="autosave"):
        """Сохраняет текущее состояние в файл"""
        data = serialize_game(player, dungeon, doors)
        # Добавляем visited, если нужно сохранить туман
        data["visited"] = dungeon.visited  # сохраняем массив посещённых тайлов
        save_path = os.path.join("saves", filename + ".json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Игра сохранена как '{filename}'")

    # ---------- ОСНОВНОЙ ЦИКЛ ----------
    while True:
        dt = clock.tick(settings.fps_limit) / 1000.0
        if dt > 0.1:
            dt = 0.1

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return False

        # ---------- ОБРАБОТКА ПАУЗЫ ----------
        if pause_menu.is_paused:
            pause_action = pause_menu.handle_input(events)

            if pause_action == "resume":
                pause_menu.toggle()
            elif pause_action == "settings":
                show_settings(screen, settings)
                screen = pygame.display.get_surface()
                sw, sh = screen.get_size()
                zoom, view_w, view_h = calc_camera_viewport(sw, sh)
                scaled_floor, scaled_moss, scaled_wall = refresh_scaled_tiles()
                pause_menu.update_screen(screen)
                pause_menu.toggle()
            elif pause_action == "save":
                # Сохраняем с именем "autosave" (можно расширить для ввода имени)
                quick_save("autosave")
                pause_menu.toggle()  # выходим из паузы после сохранения
            elif pause_action == "menu":
                return True
            elif pause_action == "quit":
                return False

            draw_scene()
            player.draw_hud(screen, font)
            pause_menu.draw()
            pygame.display.flip()
            continue

        # ---------- ОБРАБОТКА СОБЫТИЙ (НЕ ПАУЗА) ----------
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu.toggle()
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_F5:
                    # Быстрое сохранение
                    quick_save("autosave")
                elif event.key == pygame.K_e:
                    for door in doors:
                        interaction_rect = door.rect.inflate(30, 30)
                        if interaction_rect.colliderect(player.rect):
                            door.toggle()
                            break

        # ---------- ОБНОВЛЕНИЕ ----------
        keys = pygame.key.get_pressed()
        player.update_with_collision(dt, keys, dungeon, doors)
        dungeon.update_visited(player, FOG_RADIUS_TILES)
        objects_group.update(dt)
        camera_x, camera_y = update_camera(player, view_w, view_h, map_width_px, map_height_px)

        # ---------- ОТРИСОВКА ----------
        draw_scene()

        if debug_mode:
            dungeon.draw_debug(screen, camera_x, camera_y, zoom)
            debug_font = pygame.font.Font(None, 20)
            info = [
                f"FPS: {int(clock.get_fps())}",
                f"Зум: {zoom:.2f}x",
                f"Стен: {len(dungeon.collision_rects)}",
                f"Позиция: ({player.rect.x}, {player.rect.y})",
                f"Камера: ({int(camera_x)}, {int(camera_y)})",
                f"Дверей: {len(doors)}"
            ]
            for i, line in enumerate(info):
                text = debug_font.render(line, True, (255, 255, 0))
                screen.blit(text, (10, 100 + i * 20))

        player.draw_hud(screen, font)

        # Подсказки
        hint_text = "WASD / стрелки — движение    ESC — пауза    F3 — отладка    E — дверь    F5 — сохранить"
        hint = hint_font.render(hint_text, True, (150, 150, 150))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 30))

        near_door = any(door.rect.inflate(30, 30).colliderect(player.rect) and not door.is_open for door in doors)
        if near_door:
            door_hint = hint_font.render("Нажми E, чтобы открыть дверь", True, (255, 255, 100))
            screen.blit(door_hint, (sw // 2 - door_hint.get_width() // 2, sh - 60))

        pygame.display.flip()

    return True


# ============================================================
#                      ГЛАВНОЕ МЕНЮ
# ============================================================

def main():
    pygame.init()
    game_settings = GameSettings("config.json")
    flags = pygame.FULLSCREEN if game_settings.fullscreen else 0
    screen = pygame.display.set_mode((game_settings.screen_width, game_settings.screen_height), flags)
    pygame.display.set_caption("PYdangeon - Procedural Dungeon")

    while True:
        choice = show_menu(screen, game_settings)

        if choice == "start":
            char_data = show_character_select(screen, game_settings)
            if char_data is not None:
                if not game_loop(screen, game_settings, char_data=char_data):
                    break

        elif choice == "settings":
            show_settings(screen, game_settings)
            screen = pygame.display.get_surface()

        elif choice == "load":
            load_menu = LoadSaveMenu(screen, game_settings)
            result = load_menu.run()
            if result and result.startswith("load:"):
                filename = result.split(":", 1)[1]
                data = load_menu.get_save_data(filename)
                if data:
                    player, dungeon, doors = deserialize_game(data)
                    # Запускаем игру с загруженными объектами
                    if not game_loop(screen, game_settings,
                                     loaded_player=player,
                                     loaded_dungeon=dungeon,
                                     loaded_doors=doors):
                        break
                else:
                    print("❌ Ошибка загрузки сохранения")
            # Если result == "back" или None, просто продолжаем цикл

        elif choice == "exit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
