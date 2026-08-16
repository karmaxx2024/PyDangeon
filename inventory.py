import pygame


class Item:
    def __init__(self, name, icon, amount=1, description=""):
        self.name = name
        self.icon = icon
        self.amount = amount
        self.description = description


class Inventory:
    def __init__(self, screen):
        self.screen = screen

        self.opened = False

        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 22)

        # Кастомный курсор мыши
        try:
            self.cursor = pygame.image.load(
                "assets/images/menu/mouse1.png"
            ).convert_alpha()

            self.cursor_hover = pygame.image.load(
                "assets/images/menu/mouse2.png"
            ).convert_alpha()

            self.cursor = pygame.transform.smoothscale(
                self.cursor, (64, 64)
            )

            self.cursor_hover = pygame.transform.smoothscale(
                self.cursor_hover, (64, 64)
            )

        except Exception as e:
            print("Ошибка загрузки курсора:", e)
            self.cursor = None
            self.cursor_hover = None

        pygame.mouse.set_visible(False)

        self.cols = 5
        self.rows = 4

        self.slot_size = 80
        self.padding = 10

        self.selected = None

        self.items = [
            Item("Меч", "⚔", 1, "Обычный железный меч"),
            Item("Зелье", "♥", 3, "Восстанавливает здоровье"),
            Item("Монеты", "$", 25, "Золото"),
            Item("Щит", "▣", 1, "Защита"),
        ]


    def toggle(self):
        self.opened = not self.opened
        print("🎒 TOGGLE INVENTORY ->", self.opened)


    def handle_input(self, events):
        print("📦 HANDLE INPUT EVENTS:", len(events))
        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_TAB:
                    self.toggle()


            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mx, my = event.pos

                    for index in range(self.cols * self.rows):

                        x, y = self.slot_position(index)

                        rect = pygame.Rect(
                            x,
                            y,
                            self.slot_size,
                            self.slot_size
                        )

                        if rect.collidepoint(mx, my):

                            if index < len(self.items):
                                self.selected = index



    def slot_position(self, index):

        sw = self.screen.get_width()
        sh = self.screen.get_height()


        width = (
            self.cols * self.slot_size
            +
            (self.cols - 1) * self.padding
        )


        start_x = sw // 2 - width // 2
        start_y = sh // 2 - 150


        x = start_x + (
            index % self.cols
        ) * (self.slot_size + self.padding)


        y = start_y + (
            index // self.cols
        ) * (self.slot_size + self.padding)


        return x, y



    def draw(self):

        if not self.opened:
            return


        sw = self.screen.get_width()
        sh = self.screen.get_height()


        # затемнение
        dark = pygame.Surface((sw, sh))
        dark.set_alpha(170)
        dark.fill((0,0,0))

        self.screen.blit(dark,(0,0))


        # окно
        window = pygame.Rect(
            sw//2-300,
            sh//2-250,
            600,
            500
        )

        pygame.draw.rect(
            self.screen,
            (30,25,35),
            window,
            border_radius=20
        )


        pygame.draw.rect(
            self.screen,
            (220,180,70),
            window,
            4,
            border_radius=20
        )


        title = self.font.render(
            "ИНВЕНТАРЬ",
            True,
            (255,220,120)
        )

        self.screen.blit(
            title,
            (window.x+30,window.y+25)
        )


        # слоты

        for i in range(self.cols*self.rows):

            x,y = self.slot_position(i)


            color=(70,70,80)


            if self.selected == i:
                color=(180,150,50)


            pygame.draw.rect(
                self.screen,
                color,
                (x,y,self.slot_size,self.slot_size),
                border_radius=8
            )


            pygame.draw.rect(
                self.screen,
                (150,150,150),
                (x,y,self.slot_size,self.slot_size),
                2,
                border_radius=8
            )


            if i < len(self.items):

                item=self.items[i]


                icon=self.font.render(
                    item.icon,
                    True,
                    (255,255,255)
                )


                self.screen.blit(
                    icon,
                    (
                        x+25,
                        y+15
                    )
                )


                amount=self.small_font.render(
                    str(item.amount),
                    True,
                    (255,255,255)
                )


                self.screen.blit(
                    amount,
                    (
                        x+55,
                        y+55
                    )
                )


        # описание

        if self.selected is not None and self.selected < len(self.items):

            item=self.items[self.selected]

            text=self.small_font.render(
                item.name+" - "+item.description,
                True,
                (230,230,230)
            )

            self.screen.blit(
                text,
                (
                    window.x+30,
                    window.bottom-50
                )
            )

        # ---------- КАСТОМНЫЙ КУРСОР ----------
        if self.cursor and self.cursor_hover:

            mx, my = pygame.mouse.get_pos()

            hover = False

            for i in range(self.cols * self.rows):
                x, y = self.slot_position(i)

                rect = pygame.Rect(
                    x,
                    y,
                    self.slot_size,
                    self.slot_size
                )

                if rect.collidepoint(mx, my):
                    hover = True
                    break

            if hover:
                self.screen.blit(
                    self.cursor_hover,
                    (mx, my)
                )
            else:
                self.screen.blit(
                    self.cursor,
                    (mx, my)
                )