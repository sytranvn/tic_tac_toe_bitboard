from math import inf
from typing import TYPE_CHECKING, List, Literal, Tuple
from curses import wrapper, echo, cbreak

if TYPE_CHECKING:
    from curses import _CursesWindow

BitBoard = List[int]
Player = Literal[-1, 1]
Move = Tuple[float, int, int]


class InvalidMove(Exception):
    ...


def new_board(size: int) -> BitBoard:
    return [0] * size


def set_row(board: BitBoard, row: int) -> BitBoard:
    """
    Set all bit of a row to 1
    """
    new_board = board[:]
    size = len(board)
    assert row < size, "Row exceeded"
    set_row = 0
    for i in range(size):
        set_row |= 1 << i
    new_board[row] = set_row
    return new_board


def set_col(board: BitBoard, col: int) -> BitBoard:
    """
    Set all bit of a row to 1
    """
    new_board = board[:]
    size = len(board)
    assert col < size, "Column exceeded"
    for _ in range(size):
        new_board[col] |= 1 << (size - 1 - col)
    return new_board


def set_cell(board: BitBoard, row: int, col: int) -> BitBoard:
    new_board = board[:]
    size = len(board)
    assert col < size and row < size, f"Invalid cell {row}, {col}"
    new_board[row] |= 1 << (size - 1 - col)
    return new_board


def printable_board(board: BitBoard):
    size = len(board)
    return [
        [int(1 << (size - 1 - col) & board[row] != 0)
         for col in range(size)]
        for row in range(size)
    ]


def print_board(board: BitBoard):
    import pprint
    pprint.pprint(printable_board(board))


def bitboard_or(board_a, board_b) -> BitBoard:
    return [a | b for a, b in zip(board_a, board_b)]


def bitboard_and(board_a, board_b):
    return [a & b for a, b in zip(board_a, board_b)]


def bitboard_xor(board_a, board_b):
    return [a ^ b for a, b in zip(board_a, board_b)]


def is_cell_set(board, row, col):
    size = len(board)
    return (board[row] & (1 << (size - 1 - col))) != 0


def flip_cell(board, row, col):
    size = len(board)
    assert row < size and col < size, f"Invalid cell {row}, {col}"
    new_board = board[:]
    new_board[row] ^= 1 << (size - 1 - col)
    return new_board


COMP: Player = 1
HUMN: Player = -1


class TicTacToeBoard:
    def __init__(self, size: int, player='X', pieces_to_win=3) -> None:
        self.x = new_board(size)
        self.o = new_board(size)
        self.mt = new_board(size)
        self.size = size
        self.human, self.comp = (
            self.x, self.o) if player == 'X' else (self.o, self.x)
        self.players = {
            COMP: self.comp,
            HUMN: self.human,
        }
        self.winning_boards = self.make_winning_boards(pieces_to_win)

    def valid_move(self, row: int, col: int) -> bool:
        return not is_cell_set(self.mt, row, col)

    def move(self, row, col, player):
        if self.valid_move(row, col):
            self.mt = flip_cell(self.mt, row, col)
            self.players[player] = flip_cell(self.players[player], row, col)
        else:
            raise InvalidMove()

    def unmove(self, row, col, player):
        if not self.valid_move(row, col):
            self.mt = flip_cell(self.mt, row, col)
            self.players[player] = flip_cell(self.players[player], row, col)
        else:
            raise ValueError("Cannot undo a move haven't been played.")

    def make_winning_boards(self, pieces_to_win):
        boards = []
        for r in range(self.size):
            for c in range(self.size):
                if c + pieces_to_win <= self.size:
                    board = new_board(self.size)
                    for i in range(pieces_to_win):
                        try:
                            board = set_cell(board, r, c+i)
                        except InvalidMove:
                            break
                        except Exception:
                            print(r, c, i)
                            raise
                    else:
                        boards.append(board)

        for r in range(self.size):
            for c in range(self.size):
                if r + pieces_to_win <= self.size:
                    board = new_board(self.size)
                    for i in range(pieces_to_win):
                        try:
                            board = set_cell(board, r+i, c)
                        except InvalidMove:
                            break
                        except Exception:
                            print(r, c, i)
                            raise
                    else:
                        boards.append(board)

        # find forward diagonals
        #
        #        |     |  x      #
        #   -----|-----|-----    #
        #        |  *  |         #
        #   -----|-----|-----    #
        #     *  |     |         #
        #
        for r in range(self.size):
            for c in range(self.size):
                if r + pieces_to_win <= self.size and c >= pieces_to_win - 1:
                    board = new_board(self.size)
                    for i in range(pieces_to_win):
                        try:
                            board = set_cell(board, r + i, c-i)
                        except InvalidMove:
                            break
                        except Exception:
                            print(r, c, i)
                            raise

                    else:
                        boards.append(board)

        # find forward diagonals
        #
        #     x  |     |         #
        #   -----|-----|-----    #
        #        |  *  |         #
        #   -----|-----|-----    #
        #        |     |  *      #
        #
        for r in range(self.size):
            for c in range(self.size):
                if r + pieces_to_win <= self.size and c + pieces_to_win <= self.size:
                    board = new_board(self.size)
                    for i in range(pieces_to_win):
                        try:
                            board = set_cell(board, r + i, c+i)
                        except InvalidMove:
                            break
                    else:
                        boards.append(board)
        return boards

    def wins(self, player):
        player_board = self.players[player]
        for win_board in self.winning_boards:
            board = bitboard_and(player_board, win_board)
            if board == win_board:
                return True
        return False

    def heuristic(self, player: Player):
        """
        Find posible wins for player

        Posible wins are winning board that have not been interupted by opponent.
        """
        if self.wins(player):
            # set max amount of posible win states
            return player * len(self.winning_boards)

        posible_board = bitboard_or(self.players[player], self.mt)
        return player * sum([1 if bitboard_and(posible_board, win) == win else 0 for win in self.winning_boards])

    def search_alpha_beta(self, player):
        if player is COMP:
            return self.max_value(player)
        else:
            return self.min_value(player)

    def game_over(self):
        return all(r == 0 for r in self.mt) or self.wins(COMP) or self.wins(HUMN)

    def evaluate(self):
        if self.wins(COMP):
            return len(self.winning_boards)**2
        elif self.wins(HUMN):
            return -len(self.winning_boards)**2
        return 0

    def empty_cells(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if is_cell_set(self.mt, r, c)]

    def min_value(self, player: Player, alpha=-inf, beta=+inf, depth=1):
        if self.game_over():
            val = self.evaluate()
            return val, -1, -1
        # shuffle(empties)
        score, ax, ay = +inf, -1, -1
        for cell in self.empty_cells():
            x, y = cell[0], cell[1]
            self.move(x, y, player)
            m, _, _ = self.max_value(-player, alpha, beta, depth + 1)
            if m < score:
                score = m
                ax, ay = x, y
            self.unmove(x, y, player)
            if score <= alpha:
                return score, ax, ay
            beta = min(beta, score)

        return score, ax, ay

    def max_value(self, player: Player, alpha=-inf, beta=+inf, depth=1):
        if self.game_over():
            val = self.evaluate()
            return val, -1, -1
        score, ax, ay = -inf, -1, -1
        for cell in self.empty_cells():
            x, y = cell
            self.move(x, y, player)
            m, _, _ = self.min_value(-player, alpha, beta, depth + 1)
            if m > score:
                score = m
                ax, ay = x, y
            self.unmove(x, y, player)
            if score >= beta:
                return score, ax, ay
            alpha = max(alpha, score)
        return score, ax, ay

    def run(self, stdscr: "_CursesWindow"):
        stop = False
        cbreak(True)
        while not stop:
            stop = self.render(stdscr)

    def render(self, stdscr: "_CursesWindow"):
        stdscr.clear()
        for r in range(self.size):
            for c in range(self.size):
                cell = stdscr.subwin(3, 5, 3*r, 5*c)
                cell.border()
                cell.move(1, 2)
                if is_cell_set(self.x, r, c):
                    cell.addch('X')
                elif is_cell_set(self.o, r, c):
                    cell.addch('O')
                else:
                    cell.addch('.')
        stdscr.move(3*self.size + 1, 0)
        stdscr.addstr("Select cell (x, y): ")
        stdscr.refresh()
        echo()
        inp = stdscr.getstr()
        if inp == "":
            raise Exception()
        try:
            x, y = inp.split()
            x, y = int(x) - 1, int(y) - 1
            if 0 <= x <= self.size - 1 and 0 <= y <= self.size - 1:
                return x, y
            else:
                raise ValueError(f"{x}, {y}")
        except Exception:
            stdscr.addstr("Invalid cell")
        echo(False)


if __name__ == "__main__":
    wrapper(TicTacToeBoard(5, 'X', 3).run)
