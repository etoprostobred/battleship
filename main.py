from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Указанные координаты находятся вне игрового поля."


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку."


class BoardWrongShipException(BoardException):
    pass


class BoardInputException(BoardException):
    def __str__(self):
        return "Написано что-то непонятное."


class Ship:
    def __init__(self, bow, l, orientation):
        self.bow = bow
        self.l = l
        self.orientation = orientation
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            x_coord = self.bow.x
            y_coord = self.bow.y

            if self.orientation == 0:
                x_coord += i

            elif self.orientation == 1:
                y_coord += i

            ship_dots.append(Dot(x_coord, y_coord))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [ ["O"]*self.size for _ in range(self.size) ]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                coords = Dot(d.x + dx, d.y + dy)
                if not(self.out(coords)) and coords not in self.busy:
                    if verb:
                        self.field[coords.x][coords.y] = "T"
                    self.busy.append(coords)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Выстрел по координатам: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Выстрел по координатам: ").split()

            if len(coords) != 2:
                print("Введите координаты в следующем формате: две цифры, разделённые пробелом.")
                continue
            x, y = coords

            if not(x.isdigit()) or not(y.isdigit()):
                print("Это не цифры, попробуйте ещё раз.\nВведите координаты в следующем формате: две цифры, разделённые пробелом.")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        greeting = """
***********************************
*              ИГРА               *
*          «МОРСКОЙ БОЙ»          *
*        ПРИВЕТСТВУЕТ ВАС!        *
***********************************

Вы же знаете правила игры?
          """

        rools = """
Правила:
«Морской бой» — игра для двух участников.
Вашим оппонентом будет компьютер.
На игровом поле 6х6 клеток расположено
следующее количество кораблей:
1 трёхпалубный, 2 двухпалубных
и 4 однопалубных. Корабли не могут
касаться друг друга сторонами и углами.

Для совершения выстрела называются
координаты в формате х у (цифры,
разделённые пробелом). При попадании
в корабль противника — на чужом поле
ставится крестик, при холостом
выстреле — Т. Попавший стреляет ещё
раз. В случае промаха ход переходит
к сопернику.

Победителем считается тот, кто первым
потопит все семь кораблей противника.

Теперь вы готовы. Поехали!
        """

        print(greeting)

        while True:
            knowledge = input("Введите «да» или «нет»: ")
            print(f"Вы пишете: {knowledge}")

            if knowledge.lower() == "да":
                print("Окей, тогда начнём!")
                break
            if knowledge.lower() == "нет":
                print(rools)
                break
            try:
                if (knowledge.lower() != "да") and (knowledge.lower() != "нет"):
                    raise BoardInputException
            except:
                print("Не понимаю, повторите ввод!")
                print("Нужно ввести «да» или «нет».")

    def loop(self):
        num = 0
        beauty = "-"*27
        while True:
            print(f"{beauty}\nВаше поле:\n{self.us.board}")
            print(f"{beauty}\nПоле компьютера:\n{self.ai.board}")

            if num % 2 == 0:
                print(f"{beauty}\nВаш ход!")
                repeat = self.us.move()
            else:
                print(f"{beauty}\nХодит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print(f"{beauty}\nУра! Вы выиграли!")
                break

            if self.us.board.count == 7:
                print(f"{beauty}\nПам-пам-пам... Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
