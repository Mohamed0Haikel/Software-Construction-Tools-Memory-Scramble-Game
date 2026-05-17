"""
Tkinter GUI for the Memory Scramble Game.

"""

import tkinter as tk
import queue
from tkinter import messagebox, ttk

from src.config import GameConfig
from src.game_engine import GameEngine


# ─── Colour palette ───────────────────────────────────────────────────────
BG_DARK   = "#1A1A2E"
BG_BAR    = "#16213E"
CARD_BACK = "#2C3E50"
CARD_HOVER= "#34495E"
CARD_FRONT= "#ECF0F1"
CARD_MATCH= "#27AE60"
TIMER_OK  = "#E94560"
TIMER_LOW = "#FF0000"


class ConfigDialog:
    """Modal dialog for setting game parameters before starting."""

    def __init__(self, parent: tk.Tk) -> None:
        self.result: tuple[int, int, int] | None = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Game Configuration")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack()

        # --- Row count ---
        ttk.Label(frame, text="Rows (min 2):").grid(
            row=0, column=0, sticky="e", pady=5, padx=5
        )
        self.rows_var = tk.IntVar(value=4)
        ttk.Spinbox(
            frame, from_=2, to=8, textvariable=self.rows_var, width=8
        ).grid(row=0, column=1, pady=5)

        # --- Column count ---
        ttk.Label(frame, text="Columns (min 2):").grid(
            row=1, column=0, sticky="e", pady=5, padx=5
        )
        self.cols_var = tk.IntVar(value=4)
        ttk.Spinbox(
            frame, from_=2, to=8, textvariable=self.cols_var, width=8
        ).grid(row=1, column=1, pady=5)

        # --- Timeout ---
        ttk.Label(frame, text="Timeout (seconds):").grid(
            row=2, column=0, sticky="e", pady=5, padx=5
        )
        self.timeout_var = tk.IntVar(value=60)
        ttk.Spinbox(
            frame, from_=10, to=600, increment=10,
            textvariable=self.timeout_var, width=8,
        ).grid(row=2, column=1, pady=5)

        # --- Buttons ---
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(btn_frame, text="Start Game", command=self._on_ok).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side="left", padx=5
        )

        # Center on parent
        self.dialog.transient(parent)
        self.dialog.wait_window()

    def _on_ok(self) -> None:
        cfg = GameConfig(
            self.rows_var.get(),
            self.cols_var.get(),
            self.timeout_var.get(),
        )
        valid, msg = cfg.is_valid()
        if not valid:
            messagebox.showerror("Invalid Configuration", msg, parent=self.dialog)
            return
        self.result = (cfg.n_rows, cfg.n_columns, cfg.timeout_seconds)
        self.dialog.destroy()

    def _on_cancel(self) -> None:
        self.dialog.destroy()


class GameWindow:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Memory Scramble Game")
        self.root.configure(bg=BG_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.engine: GameEngine | None = None
        self.buttons: dict[tuple[int, int], tk.Button] = {}
        self._poll_id: str | None = None

        self._show_main_menu()

    # ── Main Menu ──────────────────────────────────────────────────────

    def _show_main_menu(self) -> None:
        self._stop_engine()
        self.root.geometry("420x320")

        for w in self.root.winfo_children():
            w.destroy()

        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text="🧠 Memory Scramble",
            font=("Helvetica", 26, "bold"), fg="#ECF0F1", bg=BG_DARK,
        ).pack(pady=(0, 10))
        tk.Label(
            frame, text="Find all matching pairs before time runs out!",
            font=("Helvetica", 11), fg="#BDC3C7", bg=BG_DARK,
        ).pack(pady=(0, 25))
        tk.Button(
            frame, text="▶  New Game", font=("Helvetica", 13, "bold"),
            bg="#27AE60", fg="white", activebackground="#2ECC71",
            width=16, command=self._show_config,
        ).pack(pady=4)
        tk.Button(
            frame, text="✕  Quit", font=("Helvetica", 13),
            bg="#C0392B", fg="white", activebackground="#E74C3C",
            width=16, command=self._on_close,
        ).pack(pady=4)

    # ── Config Dialog ──────────────────────────────────────────────────

    def _show_config(self) -> None:
        dlg = ConfigDialog(self.root)
        if dlg.result is not None:
            rows, cols, timeout = dlg.result
            self._start_game(rows, cols, timeout)

    # ── Start a Game ───────────────────────────────────────────────────

    def _start_game(self, n_rows: int, n_columns: int, timeout: int) -> None:
        self.engine = GameEngine(n_rows, n_columns, timeout)
        self.buttons.clear()

        for w in self.root.winfo_children():
            w.destroy()

        self._build_game_ui(n_rows, n_columns, timeout)
        self.engine.start()

        self._poll_queue()

    # ── Build the Game Board UI ────────────────────────────────────────

    def _build_game_ui(
        self, n_rows: int, n_columns: int, timeout: int
    ) -> None:
        card_px = min(80, max(44, 600 // max(n_rows, n_columns)))
        win_w = n_columns * (card_px + 8) + 60
        win_h = n_rows * (card_px + 8) + 140
        self.root.geometry(f"{win_w}x{win_h}")

        # ── Top bar (timer + moves) ──
        top = tk.Frame(self.root, bg=BG_BAR, pady=8)
        top.pack(fill="x")

        self.timer_label = tk.Label(
            top, text=f"⏱  {timeout}s",
            font=("Helvetica", 18, "bold"), fg=TIMER_OK, bg=BG_BAR,
        )
        self.timer_label.pack(side="left", padx=20)

        self.moves_label = tk.Label(
            top, text="Moves: 0",
            font=("Helvetica", 13), fg="#ECF0F1", bg=BG_BAR,
        )
        self.moves_label.pack(side="right", padx=20)

        # ── Card grid ──
        grid_frame = tk.Frame(self.root, bg=BG_DARK)
        grid_frame.pack(expand=True, fill="both", padx=15, pady=8)

        font_size = max(12, card_px // 4)

        for r in range(n_rows):
            grid_frame.grid_rowconfigure(r, weight=1)
            for c in range(n_columns):
                grid_frame.grid_columnconfigure(c, weight=1)
                btn = tk.Button(
                    grid_frame,
                    text="?",
                    font=("Helvetica", font_size, "bold"),
                    bg=CARD_BACK, fg="white",
                    activebackground=CARD_HOVER,
                    width=3, height=2,
                    relief="raised", bd=3,
                    command=lambda row=r, col=c: self._on_card_click(row, col),
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                self.buttons[(r, c)] = btn

        # ── Bottom bar ──
        bot = tk.Frame(self.root, bg=BG_BAR, pady=6)
        bot.pack(fill="x")
        tk.Button(
            bot, text="🔄 Restart", font=("Helvetica", 11),
            command=self._show_main_menu,
        ).pack(side="left", padx=20)
        tk.Button(
            bot, text="🚪 Quit", font=("Helvetica", 11),
            command=self._on_close,
        ).pack(side="right", padx=20)

    # ── Card Click Handler ─────────────────────────────────────────────

    def _on_card_click(self, row: int, col: int) -> None:
        if self.engine is None:
            return

        result = self.engine.select_card(row, col)

        if result["action"] == "ignore":
            return

        # Show the flipped card
        self._show_card(row, col, result["symbol"])

        if result.get("match"):
            r1, c1 = result["card1"]
            r2, c2 = result["card2"]
            self.buttons[(r1, c1)].configure(bg=CARD_MATCH, state="disabled")
            self.buttons[(r2, c2)].configure(bg=CARD_MATCH, state="disabled")
            self.moves_label.configure(text=f"Moves: {self.engine.moves}")

            if result.get("game_won"):
                self._on_game_won()

        elif result.get("need_flip_back"):
            r1, c1 = result["card1"]
            r2, c2 = result["card2"]
            self.moves_label.configure(text=f"Moves: {self.engine.moves}")
            # Flip back after 800 ms so the player can see both cards
            self.root.after(
                800, lambda: self._flip_back(r1, c1, r2, c2)
            )

    def _show_card(self, row: int, col: int, symbol: str) -> None:
        btn = self.buttons[(row, col)]
        btn.configure(
            text=symbol, bg=CARD_FRONT, fg="#2C3E50",
            relief="sunken", bd=2,
        )

    def _flip_back(self, r1: int, c1: int, r2: int, c2: int) -> None:
        """Flip two unmatched cards face-down again."""
        if self.engine is None:
            return
        self.engine.flip_back_selected()
        for r, c in ((r1, c1), (r2, c2)):
            self.buttons[(r, c)].configure(
                text="?", bg=CARD_BACK, fg="white",
                relief="raised", bd=3,
            )

    # ── Message-Queue Polling (Message-Passing Consumer) ───────────────

    def _poll_queue(self) -> None:
        """Drain the message queue every 100 ms.
        """
        if self.engine is None:
            return

        try:
            while True:
                msg_type, value = self.engine.message_queue.get_nowait()
                if msg_type == CountdownTimer.MSG_TICK:
                    self.timer_label.configure(text=f"⏱  {value}s")
                    if value <= 10:
                        self.timer_label.configure(fg=TIMER_LOW)
                elif msg_type == CountdownTimer.MSG_TIMEOUT:
                    self._on_timeout()
                    return  
        except queue.Empty:
            pass  

        # Schedule the next poll
        self._poll_id = self.root.after(100, self._poll_queue)

    # ── End-of-Game Handlers ───────────────────────────────────────────

    def _on_timeout(self) -> None:
        """Handle the timeout event received from the timer thread."""
        if self.engine is None:
            return

        self.engine.handle_timeout()
        self.timer_label.configure(text="⏱  0s", fg=TIMER_LOW)

        # Reveal all unmatched cards
        for r in range(self.engine.board.n_rows):
            for c in range(self.engine.board.n_columns):
                card = self.engine.board.get_card(r, c)
                if not card.is_matched:
                    self._show_card(r, c, card.symbol)
                    self.buttons[(r, c)].configure(
                        state="disabled", bg="#7F8C8D"
                    )

        messagebox.showinfo(
            "Game Over!",
            "⏰ Time's up!\nYou didn't find all the matching pairs.",
        )
        self._show_main_menu()

    def _on_game_won(self) -> None:
        """Handle a win (all pairs matched before timeout)."""
        if self.engine is None:
            return
        time_left = self.engine._timer.time_remaining if self.engine._timer else 0
        messagebox.showinfo(
            "🎉 Congratulations!",
            f"You found all matching pairs!\n\n"
            f"Moves: {self.engine.moves}\n"
            f"Time remaining: {time_left}s",
        )
        self._show_main_menu()

    # ── Cleanup ────────────────────────────────────────────────────────

    def _stop_engine(self) -> None:
        if self._poll_id is not None:
            self.root.after_cancel(self._poll_id)
            self._poll_id = None
        if self.engine is not None:
            self.engine.stop()
            self.engine = None

    def _on_close(self) -> None:
        self._stop_engine()
        self.root.destroy()



from src.timer import CountdownTimer  