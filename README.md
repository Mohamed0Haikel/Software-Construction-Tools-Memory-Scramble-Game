# Memory Scramble Game

A card-matching memory game built with Python and Tkinter, demonstrating
concurrency concepts from the Software Construction course.

---

##  Requirements

- **Python 3.10+** (uses modern type hints)
- No external packages required — the game uses only the Python standard library:
  - `tkinter`
  - `threading`
  - `queue`
  - `unittest`

---

##  How to Build & Run

### 1. Clone the Repository

```bash
git clone https://github.com/Mohamed0Haikel/Software-Construction-Tools-Memory-Scramble-Game.git
cd memory-scramble-game
```

### 2. Run the Game

```bash
python -m src.main
```

### 3. Play the Game

1. Click **New Game**
2. Configure:
   - Rows
   - Columns
   - Timeout
3. Click **Start Game**
4. Flip cards and match all pairs before the timer reaches zero!

---

## Project Architecture

```text
memory-scramble-game/
├── README.md
├── requirements.txt
└── src/
    ├── main.py         # Entry point
    ├── config.py       # GameConfig dataclass & SYMBOLS
    ├── board.py        # Board & Card domain models
    ├── timer.py        # CountdownTimer (thread + lock + queue)
    ├── game_engine.py  # Thread-safe game state manager
    └── gui.py          # Tkinter GUI (queue consumer)
```

---


- Uses only Python standard library modules

---
