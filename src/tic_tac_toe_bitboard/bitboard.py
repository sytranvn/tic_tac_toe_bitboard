from typing import List

BitBoard = List[int]


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


class TicTacToeBoard:
    def __init__(self, size: int, first='X', pieces_to_win=3) -> None:
        self.x = new_board(size)
        self.o = new_board(size)
        self.mt = new_board(size)
        self.size = size
        self.players = [self.x, self.o] if first == 'X' else [self.o, self.x]
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

    def heuristic(self, player):
        """
        Find posible wins for player

        Posible wins are winning board that have not been interupted by opponent.
        """

    def game_over(self):
        return True
