import pygame
import math
from settings import *


# ============================================================
#                    ТИПЫ МОБОВ
# ============================================================

MOB_TYPES = {

    "goblin": {
        "name": "Гоблин",
        "hp": 40,
        "damage": 8,
        "speed": 90,
        "aggro": 250,
        "attack_range": 45,
        "attack_delay": 1.0,
        "color": (200, 40, 40),
        "size": 24
    },


    "orc": {
        "name": "Орк",
        "hp": 120,
        "damage": 18,
        "speed": 55,
        "aggro": 300,
        "attack_range": 55,
        "attack_delay": 1.4,
        "color": (80, 160, 60),
        "size": 34
    }

}


# ============================================================
#                       MOB CLASS
# ============================================================


class Mob:

    def __init__(self, x, y, mob_type="goblin"):


        data = MOB_TYPES.get(
            mob_type,
            MOB_TYPES["goblin"]
        )


        # позиция
        self.x = float(x)
        self.y = float(y)


        # данные
        self.type = mob_type
        self.name = data["name"]

        self.max_hp = data["hp"]
        self.hp = data["hp"]

        self.damage = data["damage"]

        self.speed = data["speed"]

        self.aggro_radius = data["aggro"]

        self.attack_range = data["attack_range"]

        self.attack_delay = data["attack_delay"]

        self.color = data["color"]

        self.size = data["size"]



        # состояние AI

        self.state = "IDLE"


        # атака

        self.attack_timer = 0



        # получение урона

        self.hit_timer = 0



        # жив?

        self.dead = False



        # хитбокс

        self.rect = pygame.Rect(
            0,
            0,
            self.size,
            self.size
        )

        self.rect.center = (
            int(self.x),
            int(self.y)
        )



    # ========================================================
    # UPDATE
    # ========================================================


    def update(self, dt, player, dungeon):


        if self.dead:
            return



        if self.attack_timer > 0:
            self.attack_timer -= dt


        if self.hit_timer > 0:
            self.hit_timer -= dt



        dx = player.x - self.x
        dy = player.y - self.y


        distance = math.sqrt(
            dx * dx +
            dy * dy
        )



        # ----------------------------
        # AI
        # ----------------------------


        if distance <= self.aggro_radius:


            if distance <= self.attack_range:

                self.state = "ATTACK"

                self.attack(player)


            else:

                self.state = "CHASE"

                self.move_to_player(
                    dx,
                    dy,
                    distance,
                    dt,
                    dungeon
                )


        else:

            self.state = "IDLE"



    # ========================================================
    # ДВИЖЕНИЕ
    # ========================================================


    def move_to_player(
            self,
            dx,
            dy,
            distance,
            dt,
            dungeon
    ):


        if distance == 0:
            return


        dx /= distance
        dy /= distance


        move_x = dx * self.speed * dt
        move_y = dy * self.speed * dt



        # X движение

        self.x += move_x

        self.rect.centerx = int(self.x)


        if dungeon.check_collision(
                self.rect,
                0,
                0
        ):

            self.x -= move_x
            self.rect.centerx = int(self.x)



        # Y движение


        self.y += move_y

        self.rect.centery = int(self.y)


        if dungeon.check_collision(
                self.rect,
                0,
                0
        ):

            self.y -= move_y
            self.rect.centery = int(self.y)



    # ========================================================
    # АТАКА
    # ========================================================


    def attack(self, player):


        if self.attack_timer > 0:
            return



        player.take_damage(
            self.damage
        )


        self.attack_timer = self.attack_delay


        print(
            f"{self.name} атакует игрока!"
        )



    # ========================================================
    # УРОН
    # ========================================================


    def take_damage(self, damage):


        if self.dead:
            return



        self.hp -= damage


        self.hit_timer = 0.15



        print(
            f"{self.name} получил {damage} урона. HP {self.hp}/{self.max_hp}"
        )



        if self.hp <= 0:

            self.hp = 0
            self.dead = True

            print(
                f"{self.name} умер"
            )



    # ========================================================
    # ПРОВЕРКА ЖИЗНИ
    # ========================================================


    def is_alive(self):

        return not self.dead



    # ========================================================
    # ОТРИСОВКА
    # ========================================================


    def draw_with_camera(
            self,
            screen,
            camera_x,
            camera_y,
            zoom=1.0
    ):


        x = int(
            (self.x-camera_x)
            * zoom
        )

        y = int(
            (self.y-camera_y)
            * zoom
        )



        size = int(
            self.size * zoom
        )



        color = self.color


        # эффект получения урона

        if self.hit_timer > 0:

            color = WHITE



        pygame.draw.rect(
            screen,
            color,
            (
                x-size//2,
                y-size//2,
                size,
                size
            )
        )



        # HP полоска


        bar_w = int(40 * zoom)
        bar_h = max(
            3,
            int(5*zoom)
        )


        bar_x = x - bar_w//2

        bar_y = y - size//2 - 10



        pygame.draw.rect(
            screen,
            (70,0,0),
            (
                bar_x,
                bar_y,
                bar_w,
                bar_h
            )
        )



        hp_width = int(
            bar_w *
            self.hp /
            self.max_hp
        )


        pygame.draw.rect(
            screen,
            (0,220,0),
            (
                bar_x,
                bar_y,
                hp_width,
                bar_h
            )
        )



    # ========================================================
    # RECT
    # ========================================================


    def get_rect(self):

        return self.rect