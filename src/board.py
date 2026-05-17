"""
Board and Card domain models.

"""

import random
from src.config import SYMBOLS


class Card:
    """A single card on the game board."""

    def __init__(self, symbol: str, row: int, col: int) -> None:
        self.symbol: str = symbol
        self.row: int = row
        self.col: int = col
        self.is_face_up: bool = False
        self.is_matched: bool = False

    def flip_up(self) -> None:
        self.is_face_up = True

    def flip_down(self) -> None:
        if not self.is_matched:
            self.is_face_up = False

    def mark_matched(self) -> None:
        self.is_matched = True
        self.is_face_up = True

    def __repr__(self) -> str:
        state = "M" if self.is_matched else ("U" if self.is_face_up else "D")
        return f"Card({self.symbol}@{self.row},{self.col}={state})"


class Board:
    """The game board — a 2-D grid of Cards."""

    def __init__(self, n_rows: int, n_columns: int) -> None:
        self.n_rows: int = n_rows
        self.n_columns: int = n_columns
        self.grid: list[list[Card]] = []
        self._generate()


    def _generate(self) -> None:
        """Create pairs of symbols and shuffle them onto the grid."""
        num_pairs = (self.n_rows * self.n_columns) // 2
        symbols = SYMBOLS[:num_pairs] * 2        
        random.shuffle(symbols)

        self.grid = []
        idx = 0
        for r in range(self.n_rows):
            row: list[Card] = []
            for c in range(self.n_columns):
                row.append(Card(symbols[idx], r, c))
                idx += 1
            self.grid.append(row)


    def get_card(self, row: int, col: int) -> Card:
        return self.grid[row][col]

    def all_matched(self) -> bool:
        """Return True when every card on the board is matched."""
        return all(card.is_matched for row in self.grid for card in row)

    def reset(self) -> None:
        """Re-shuffle the board for a new game."""
        for row in self.grid:
            for card in row:
                card.is_face_up = False
                card.is_matched = False
        self._generate()