"""
Game engine — thread-safe orchestrator for game logic.

"""

import threading
import queue

from src.board import Board
from src.timer import CountdownTimer


class GameEngine:
    """Manages the core game state and rules."""

    def __init__(
        self,
        n_rows: int,
        n_columns: int,
        timeout_seconds: int,
    ) -> None:
        self.board = Board(n_rows, n_columns)
        self.timeout = timeout_seconds

    
        self._message_queue: queue.Queue = queue.Queue()

        
        self._lock = threading.Lock()

        self._selected_cards: list = []
        self._game_over: bool = False
        self._game_won: bool = False
        self._moves: int = 0
        self._processing: bool = False  

        self._timer: CountdownTimer | None = None


    @property
    def message_queue(self) -> queue.Queue:
        return self._message_queue

    @property
    def game_over(self) -> bool:
        with self._lock:
            return self._game_over

    @property
    def game_won(self) -> bool:
        with self._lock:
            return self._game_won

    @property
    def moves(self) -> int:
        with self._lock:
            return self._moves


    def start(self) -> None:
        """Start the countdown timer in its own thread."""
        self._timer = CountdownTimer(self.timeout, self._message_queue)
        self._timer.start()

    def stop(self) -> None:
        """Stop the timer thread (called on window close / restart)."""
        if self._timer is not None:
            self._timer.stop()


    def select_card(self, row: int, col: int) -> dict:
        """Handle the player clicking on a card.
        """
        with self._lock:
            if self._game_over or self._processing:
                return {"action": "ignore"}

            card = self.board.get_card(row, col)

            if card.is_face_up or card.is_matched:
                return {"action": "ignore"}

            card.flip_up()
            self._selected_cards.append(card)

            result: dict = {
                "action": "flip",
                "row": row,
                "col": col,
                "symbol": card.symbol,
            }

            if len(self._selected_cards) == 2:
                self._moves += 1
                card1, card2 = self._selected_cards

                if card1.symbol == card2.symbol:
                    card1.mark_matched()
                    card2.mark_matched()
                    result["match"] = True
                    result["card1"] = (card1.row, card1.col)
                    result["card2"] = (card2.row, card2.col)
                    self._selected_cards.clear()

                    if self.board.all_matched():
                        self._game_over = True
                        self._game_won = True
                        if self._timer:
                            self._timer.stop()
                        result["game_won"] = True
                else:
                    result["match"] = False
                    result["card1"] = (card1.row, card1.col)
                    result["card2"] = (card2.row, card2.col)
                    self._processing = True
                    result["need_flip_back"] = True

            return result

    def flip_back_selected(self) -> None:
        """Flip the two unmatched cards back face-down.
        """
        with self._lock:
            for card in self._selected_cards:
                card.flip_down()
            self._selected_cards.clear()
            self._processing = False

    def handle_timeout(self) -> None:
        """Called when the countdown timer reaches zero."""
        with self._lock:
            self._game_over = True
            self._game_won = False