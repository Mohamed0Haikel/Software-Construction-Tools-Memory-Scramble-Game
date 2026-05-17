"""
Game configuration and constants.

"""

from dataclasses import dataclass

# board_size/2 unique symbols are needed for a game.
SYMBOLS: list[str] = [
    "♠", "♥", "♦", "♣", "★", "♪", "☀", "☁",
    "✿", "❤","✦", "✓", "✗", "❖", "☘",
]


@dataclass
class GameConfig:
    """Immutable configuration for a single game session."""

    n_rows: int = 4
    n_columns: int = 4
    timeout_seconds: int = 60

    @property
    def board_size(self) -> int:
        return self.n_rows * self.n_columns

    @property
    def num_pairs(self) -> int:
        return self.board_size // 2

    def is_valid(self) -> tuple[bool, str]:
        """Validate the configuration; return (ok, error_message)."""
        if self.n_rows < 2 or self.n_columns < 2:
            return False, "Rows and columns must be at least 2."
        if self.board_size % 2 != 0:
            return False, "Total board size (rows × columns) must be even."
        if self.num_pairs > len(SYMBOLS):
            return False, (
                f"Board too large — max {len(SYMBOLS)} pairs supported "
                f"(got {self.num_pairs})."
            )
        if self.timeout_seconds < 5:
            return False, "Timeout must be at least 5 seconds."
        return True, ""