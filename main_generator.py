import random


class MazeGenerator:
    """Генератор лабиринта DFS с комнатами."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.maze = []
        self.rooms = []


    def _create_room(self, x, y, w, h):

        self.rooms.append((x, y, w, h))

        for yy in range(y, y + h):
            for xx in range(x, x + w):

                if (
                    0 < xx < self.width - 1
                    and
                    0 < yy < self.height - 1
                ):
                    self.maze[yy][xx] = False

    def _generate_rooms(self):

        size = min(7, self.width // 5, self.height // 5)
        size = max(3, size)

        # =====================
        # ЛЕВАЯ ВЕРХНЯЯ
        # =====================

        x = random.randint(
            2,
            max(2, self.width // 3 - size)
        )

        y = random.randint(
            2,
            max(2, self.height // 3 - size)
        )

        self._create_room(
            x,
            y,
            size,
            size
        )

        # =====================
        # ЦЕНТР
        # =====================

        x = self.width // 2 - size // 2
        y = self.height // 2 - size // 2

        self._create_room(
            x,
            y,
            size,
            size
        )

        # =====================
        # ПРАВАЯ НИЖНЯЯ
        # =====================

        x_min = self.width * 2 // 3
        x_max = self.width - size - 2

        y_min = self.height * 2 // 3
        y_max = self.height - size - 2

        # если карта маленькая
        # ставим комнату максимально близко к краю

        x = random.randint(
            min(x_min, x_max),
            x_max
        )

        y = random.randint(
            min(y_min, y_max),
            y_max
        )

        self._create_room(
            x,
            y,
            size,
            size
        )

    def _add_doors(self):

        for x, y, w, h in self.rooms:

            side = random.choice(
                [
                    "top",
                    "bottom",
                    "left",
                    "right"
                ]
            )


            if side == "top" and y > 1:

                dx = random.randint(
                    x + 1,
                    x + w - 2
                )

                self.maze[y-1][dx] = False


            elif side == "bottom" and y+h < self.height-1:

                dx = random.randint(
                    x + 1,
                    x+w-2
                )

                self.maze[y+h][dx] = False


            elif side == "left" and x > 1:

                dy = random.randint(
                    y+1,
                    y+h-2
                )

                self.maze[dy][x-1] = False


            elif side == "right" and x+w < self.width-1:

                dy = random.randint(
                    y+1,
                    y+h-2
                )

                self.maze[dy][x+w] = False



    def generate(self):

        self.maze = [
            [True for _ in range(self.width)]
            for _ in range(self.height)
        ]


        self.rooms = []



        # ===== СТАРЫЙ DFS =====

        start_x = 1
        start_y = 1


        self.maze[start_y][start_x] = False


        stack = [
            (start_x, start_y)
        ]


        visited = {
            (start_x, start_y)
        }



        while stack:

            x, y = stack[-1]

            neighbors = []


            for dx, dy in [
                (0,-2),
                (0,2),
                (-2,0),
                (2,0)
            ]:

                nx = x + dx
                ny = y + dy


                if (
                    0 < nx < self.width-1
                    and
                    0 < ny < self.height-1
                    and
                    (nx,ny) not in visited
                ):

                    neighbors.append(
                        (nx,ny,dx,dy)
                    )



            if neighbors:

                nx,ny,dx,dy = random.choice(
                    neighbors
                )


                self.maze[
                    y+dy//2
                ][
                    x+dx//2
                ] = False


                self.maze[ny][nx] = False


                visited.add(
                    (nx,ny)
                )


                stack.append(
                    (nx,ny)
                )


            else:

                stack.pop()



        # ===== ДОБАВЛЯЕМ КОМНАТЫ =====

        self._generate_rooms()


        self._add_doors()



        # границы

        for y in range(self.height):

            self.maze[y][0] = True
            self.maze[y][-1] = True


        for x in range(self.width):

            self.maze[0][x] = True
            self.maze[-1][x] = True



        return self.maze
