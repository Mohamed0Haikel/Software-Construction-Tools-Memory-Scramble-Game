```markdown
# Memory Scramble Game

A card-matching memory game built with Python and Tkinter, demonstrating
concurrency concepts from the Software Construction course.

---

## Requirements

- **Python 3.10+** (uses modern type hints)
- No external packages required — the game uses only the Python standard
  library (`tkinter`, `threading`, `queue`, `unittest`).


---

## How to Build & Run

1. **Clone the repository:**
   ```
   git clone https://github.com/Mohamed0Haikel/Software-Construction-Tools-Memory-Scramble-Game.git
   cd memory-scramble-game
   ```

2. **Run the game:**
   ```
   python -m src.main
   ```

3. **Play:**
   - Click **New Game** → configure rows, columns, and timeout → **Start Game**.
   - Click cards to flip them. Find all matching pairs before the timer reaches zero!


---

## Project Architecture


memory-scramble-game/
├── README.md                 
├── requirements.txt
└── src/
    ├── main.py               : entry point
    ├── config.py             : GameConfig dataclass & SYMBOLS
    ├── board.py              : Board & Card domain models
    ├── timer.py              : CountdownTimer (thread + lock + queue)
    ├── game_engine.py        : thread-safe game state manager
    └── gui.py                : Tkinter GUI (queue consumer)


---



