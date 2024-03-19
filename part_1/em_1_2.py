import random


class Cell:
    def __init__(self) -> None:
        self.around_mines: int = 0
        self.mine: bool = False
        self.fl_open: bool = False


class GamePole:
    def __init__(self, fields: int, mines: int) -> None:
        self.fields = fields
        self.mines = mines
        self.pole = [[Cell() for _ in range(fields)] for _ in range(fields)]
        self.empty_cells = fields ** 2 - mines
        self.place_mines()

    def place_mines(self) -> None:
        mine_positions = random.sample(range(self.fields ** 2), self.mines)
        for position in mine_positions:
            row = position // self.fields
            col = position % self.fields
            self.pole[row][col].mine = True
            self.increment_around_mines(row, col)

    def increment_around_mines(self, row, col) -> None:
        for i in range(max(0, row - 1), min(row + 2, self.fields)):
            for j in range(max(0, col - 1), min(col + 2, self.fields)):
                if not (i == row and j == col):
                    self.pole[i][j].around_mines += 1

    def open_cell(self, row, col) -> bool:
        cell = self.pole[row][col]
        if cell.fl_open:
            return False
        cell.fl_open = True
        self.empty_cells -= 1
        if cell.mine:
            return True
        if cell.around_mines == 0:
            for i in range(max(0, row - 1), min(row + 2, self.fields)):
                for j in range(max(0, col - 1), min(col + 2, self.fields)):
                    if not (i == row and j == col):
                        self.open_cell(i, j)
        return False

    def show(self) -> None:
        for row in self.pole:
            for cell in row:
                if cell.fl_open:
                    if cell.mine:
                        print("*", end=" ")
                    else:
                        print(cell.around_mines, end=" ")
                else:
                    print("#", end=" ")
            print()
        print("------")

    def play_game(self):
        while True:
            try:
                row = int(input("Введите номер строки: "))
                col = int(input("Введите номер столбца: "))
                if row <= 0 or col <= 0:
                    raise ValueError
                if self.open_cell(row - 1, col - 1):
                    self.show()
                    print("БОМБА!!!")
                    break
                else:
                    self.show()
                    if self.empty_cells == 0:
                        print("Победа!")
                        break
                    print("Двигаемся дальше!")
            except ValueError:
                print("Ошибка! Введите положительное число!")
            except IndexError:
                print("Указанной клетки нет на игровом поле!")


fields = 10
mines = 12
pole_game = GamePole(fields, mines)
pole_game.play_game()
