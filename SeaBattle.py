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
        return "You are trying to shoot out of the board!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You have already shot this cell"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
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

    def __str__(self):
        res = "x/y| 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

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
                    self.contour(ship)
                    print("Ship destroyed!")
                    return True  # Возвращаем True, если попадание
                else:
                    print("Ship was hit!")
                    return True  # Возвращаем True, если попадание

        self.field[d.x][d.y] = "T"  # Используем букву T для промахов
        print("Miss!")
        return False  # Возвращаем False, если промах

    def contour(self, ship):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy and self.field[cur.x][cur.y] == "O":
                    self.field[cur.x][cur.y] = "T"

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy, name):
        self.board = board
        self.enemy = enemy
        self.name = name

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


class User(Player):
    def ask(self):
        while True:
            cords = input(f"{self.name}, your move (format: x y): ").split()

            if len(cords) != 2:
                print("Enter 2 coordinates!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Enter numbers!")
                continue

            x, y = int(x), int(y)

            if x < 1 or x > self.board.size or y < 1 or y > self.board.size:
                print("Coordinates are out of range!")
                continue

            return Dot(x - 1, y - 1)


class AI_System(Player):
    def ask(self):
        x = randint(0, 5)
        y = randint(0, 5)
        print(f"Computer-pirate's move: {x + 1} {y + 1}")
        return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.player_name = ""
        self.ai = None
        self.us = None

    def greet(self):
        print(f"Welcome to the Sea Battle Game, commander!")
        print("-------------------")
        print("Write coordinates to place your symbol in x y format!")
        print("-------------------")
        print("Press Enter to start your game!")
        print("-------------------")
        input()
        self.player_name = input("Enter your name, commander: ")

    def show_board_options(self):
        options = []
        for _ in range(3):  # Number of board options
            board = self.random_board()
            options.append(board)

        option_index = 0
        while True:
            print(f"Choose your starting board, {self.player_name}! Board option {option_index + 1}:")
            print(options[option_index])
            print("-------------------")
            print("Type 'Next' to see the next option or 'Ok' to select this board.")
            choice = input("Your choice: ").strip().lower()
            if choice == 'next':
                option_index = (option_index + 1) % len(options)
            elif choice == 'ok':
                return options[option_index]
            else:
                print("Invalid input! Please type 'Next' or 'Ok'.")

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print(f"{self.player_name}'s board:")
            print(self.us.board)
            print("-" * 20)
            print("Computer-pirate's board:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print(f"{self.player_name}'s turn!")
                repeat = self.us.move()
                if not repeat:
                    num += 1
            else:
                print("-" * 20)
                print("Computer-pirate's turn!")
                repeat = self.ai.move()
                if not repeat:
                    num += 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print(f"{self.player_name} won!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Computer-pirate won! Try again, commander")
                break

    def start(self):
        self.greet()
        ai_board = self.random_board()
        user_board = self.show_board_options()
        self.us = User(user_board, ai_board, self.player_name)
        self.ai = AI_System(ai_board, self.us.board, "Computer-pirate")
        self.ai.board.hid = True
        self.loop()


if __name__ == "__main__":
    g = Game()
    g.start()
