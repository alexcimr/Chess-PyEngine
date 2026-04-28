# Chess PyEngine

![Gameplay](assets/gameplay.gif)

A custom **chess engine** and playable GUI written from scratch in **Python**.
It uses optimized **Minimax search**, custom **piece-square tables**, and an **opening book** trained on master-level games.

---

## Engine Features

- **Minimax with Alpha-Beta pruning**: The core search algorithm enhanced with move ordering (captures first) to maximize pruning.
- **Quiescence Search**: Resolves the **horizon effect** and prevents the engine from making blunders at the end of its search depth by searching deeper on capture sequences. Includes a **standing pat** condition.
- **Transposition Tables**: Caches evaluated positions via **Zobrist hashing** to skip redundant calculations and significantly boost search speed.
- **Piece-Square Tables**: Generated from 100,000 master games using the [Lichess Elite Database](https://database.nikonoel.fr/). Features separate weights for opening, midgame, and endgame, with down-weighted starting squares to prevent overvaluing unmoved pieces.
- **Opening Book**: Built from the same PGN dataset, mapped to **Zobrist hashes**. The bot samples moves based on their real-world frequency rather than always playing the absolute most common move.
- **Dynamic Search Depth**: Automatically increases search depth as material leaves the board, allowing for deeper endgame calculations.
---

## Stack

- **Python 3**
- **Pygame** (Graphical Interface)
- **python-chess** (PGN Parsing)
- **pytest** (Unit Testing)

---

## Project Structure

```text
Chess/
├── assets/
│   └── gameplay.gif     # demo animation for README
├── data/
│   ├── book.json
│   ├── book.py          # builds opening book from PGN
│   ├── pst.json
│   └── pst.py           # builds PST from PGN
├── model/
│   ├── pieces/          # move generation per piece type
│   ├── board.py         # board state, move logic, Zobrist hashing
│   ├── bot.py           # Minimax engine
│   ├── enums.py
│   └── utils.py
├── tests/
│   ├── test_board.py
│   ├── test_bot.py
│   └── test_pieces.py
├── game.py              # Game GUI logic
├── main.py
└── README.md
```

---

## Setup & Usage

```bash
pip install pygame python-chess pytest
python main.py
```

You play as White. Click a piece to select it, then click a destination square. The engine will automatically respond.
## Running tests
```bash
python -m pytest tests/ -v
```

## Retraining the datasets
To retrain using a different dataset, download a PGN file and update the `PGN_FILE` path in the scripts:

```bash
python data/book.py
python data/pst.py
```

---

## Future Roadmap
- **Neural Network Eval**: Replace the static PST with a shallow neural network for more precise positional scoring.
- **GUI Improvements**: Add a move history log, color selection, and timer.