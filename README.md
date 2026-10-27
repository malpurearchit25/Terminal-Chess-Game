# Terminal Chess

A two-player chess game for the terminal, built with Python and the standard library. It includes a Unicode board, legal-move highlighting, check and checkmate detection, pawn promotion, castling, en passant, captured-piece tracking, and optional celebration animations.

## Requirements

- Python 3.10 or newer
- A terminal with ANSI color and Unicode chess-symbol support (Windows Terminal, PowerShell 7, macOS Terminal, or a modern Linux terminal)

No third-party packages are required.

## Run

```sh
python Chess.py
```

On Windows, if `python` is not on PATH:

```powershell
py -3 Chess.py
```

Skip the animated intro and end screens with `--no-animation`:

```sh
python Chess.py --no-animation
```

At the board, type a square such as `e2` to select a piece, then its destination such as `e4`. You can also enter a full move such as `e2e4` after selecting a piece. Enter the selected square again to deselect it; enter `q` to quit. When a pawn reaches the last rank, choose `q`, `r`, `b`, or `n` for its promotion piece.

## Rules implemented

Legal movement for all pieces, check prevention, checkmate and stalemate, castling, en passant, and promotion. Castling rights are removed when the king or an original rook moves, or when an original rook is captured. En passant is available only on the immediately following turn and cannot expose the moving king to check.

This learning project does not yet implement threefold repetition, the fifty-move rule, or draw claims for insufficient material. Moves use coordinate notation rather than algebraic notation. The visual board requires a reasonably wide terminal; `--no-animation` works well in smaller windows.

## Tests

Run the standard-library test suite:

```sh
python -m unittest discover -s tests -t . -v
```

Tests cover the initial legal move count, input parsing, king safety, castling, en passant, checkmate, and stalemate. GitHub Actions runs the suite on Windows and Linux.

## Project files

```text
Chess.py                 Game, board renderer, and rule logic
tests/test_chess.py      Rule and input regression tests
.github/workflows/test.yml  Windows and Linux checks
```

The accompanying coursework document was used as background context and is not needed to run the game.
