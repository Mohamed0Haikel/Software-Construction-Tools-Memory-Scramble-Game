#!/usr/bin/env python3
"""
Entry point for the Memory Scramble Game.

Run with:  python -m src.main
"""

import tkinter as tk
from src.gui import GameWindow


def main() -> None:
    root = tk.Tk()
    root.title("Memory Scramble Game")
    root.geometry("420x320")
    root.configure(bg="#1A1A2E")
    root.resizable(True, True)

    _app = GameWindow(root)   
    root.mainloop()


if __name__ == "__main__":
    main()