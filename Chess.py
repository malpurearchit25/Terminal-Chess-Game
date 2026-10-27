import argparse
import os
import re
import time
import sys
import random
import math

SIZE = 8

# ─── ANSI COLORS ───────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

BG_DARK      = "\033[48;2;101;67;33m"
BG_LIGHT     = "\033[48;2;222;184;135m"
BG_SELECTED  = "\033[48;2;240;200;50m"
BG_VALID     = "\033[48;2;120;180;80m"
BG_LASTMOVE  = "\033[48;2;170;210;100m"
BG_CHECK     = "\033[48;2;200;50;50m"
BG_CAPTURE   = "\033[48;2;200;100;50m"

TXT_WHITE_PIECE = "\033[1;38;2;255;255;255m"
TXT_BLACK_PIECE = "\033[1;38;2;28;14;4m"

C_GOLD   = "\033[38;2;212;175;55m"
C_WHITE  = "\033[97m"
C_DIM    = "\033[2;37m"
C_RED    = "\033[1;31m"
C_GREEN  = "\033[1;32m"
C_YELLOW = "\033[1;33m"
C_CYAN   = "\033[1;36m"
C_MAGENTA= "\033[1;35m"
C_BLUE   = "\033[1;34m"

FIREWORK_COLORS = [C_RED, C_YELLOW, C_GREEN, C_CYAN, C_MAGENTA, C_BLUE, C_WHITE]
SPARKS = ['*', '+', '·', '✦', '✸', '✺', '❋', '✻', '★', '•', '◆', '▪']

board = [[0]*SIZE for _ in range(SIZE)]
castling_rights = {"K": True, "Q": True, "k": True, "q": True}
en_passant_target = None
SKIP_ANIMATIONS = False

WHITE_SYMBOLS = {1:"♙", 2:"♖", 3:"♘", 4:"♗", 5:"♕", 6:"♔"}
BLACK_SYMBOLS = {1:"♟", 2:"♜", 3:"♞", 4:"♝", 5:"♛", 6:"♚"}

# ═══════════════════════════════════════════════════════════════════════════════
#  BOARD SIZING  ← increase these to make squares bigger
# ═══════════════════════════════════════════════════════════════════════════════
SQ_W = 7    # total width  of each square in characters (must be odd for centring)
SQ_H = 3    # total height of each square in lines      (must be odd for centring)

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def clear(): os.system("cls" if os.name == "nt" else "clear")

def hide_cursor(): sys.stdout.write("\033[?25l"); sys.stdout.flush()
def show_cursor(): sys.stdout.write("\033[?25h"); sys.stdout.flush()

def move_cursor(row, col):
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()

def print_at(row, col, text):
    move_cursor(row, col)
    sys.stdout.write(text)
    sys.stdout.flush()

def typewrite(text, delay=0.03, color=""):
    for ch in text:
        sys.stdout.write(color + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.lines, size.columns
    except:
        return 50, 100

# ═══════════════════════════════════════════════════════════════════════════════
#  WELCOME ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════
TITLE_ART = r"""\n   ██████╗██╗  ██╗███████╗███████╗███████╗\n  ██╔════╝██║  ██║██╔════╝██╔════╝██╔════╝\n  ██║     ███████║█████╗  ███████╗███████╗\n  ██║     ██╔══██║██╔══╝  ╚════██║╚════██║\n  ╚██████╗██║  ██║███████╗███████║███████║\n   ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝\n"""

CHESS_PIECES_ART = [
    "    ♚  ♛  ♜  ♝  ♞  ♟    ",
    "    ♔  ♕  ♖  ♗  ♘  ♙    ",
]

def fade_in_title():
    if SKIP_ANIMATIONS:
        clear()
        print(C_GOLD + BOLD + "CHESS" + RESET)
        print(C_DIM + "The classic game of strategy" + RESET)
        input(C_GOLD + "\nPress Enter to begin" + RESET)
        return
    lines = TITLE_ART.strip('\n').split('\n')
    rows, cols = get_terminal_size()
    start_col = max(1, (cols - 42) // 2)
    start_row = max(1, (rows - 18) // 2)

    hide_cursor()
    clear()

    for i, line in enumerate(lines):
        print_at(start_row + i, start_col, C_DIM + line + RESET)
    time.sleep(0.3)

    gold_codes = [
        "\033[38;2;100;80;20m",
        "\033[38;2;150;120;30m",
        "\033[38;2;190;155;40m",
        "\033[38;2;212;175;55m",
        "\033[38;2;240;210;100m",
        "\033[38;2;255;240;160m",
        "\033[38;2;212;175;55m",
    ]

    max_len = max(len(l) for l in lines)
    for col_offset in range(max_len + len(gold_codes)):
        for i, line in enumerate(lines):
            row_out = []
            for ci, ch in enumerate(line):
                dist = col_offset - ci
                if 0 <= dist < len(gold_codes):
                    row_out.append(gold_codes[dist] + BOLD + ch + RESET)
                elif dist >= len(gold_codes):
                    row_out.append(C_GOLD + BOLD + ch + RESET)
                else:
                    row_out.append(C_DIM + ch + RESET)
            print_at(start_row + i, start_col, ''.join(row_out))
        time.sleep(0.018)

    piece_row = start_row + len(lines) + 1
    print_at(piece_row, start_col + 8, C_DIM + CHESS_PIECES_ART[1] + RESET)
    time.sleep(0.2)

    pieces = [("♔","♚"), ("♕","♛"), ("♖","♜"), ("♗","♝"), ("♘","♞"), ("♙","♟")]
    base_col = start_col + 11
    for idx, (wp, bp) in enumerate(pieces):
        col = base_col + idx * 3
        print_at(piece_row,     col, TXT_WHITE_PIECE + BOLD + wp + RESET)
        print_at(piece_row + 1, col, TXT_BLACK_PIECE + BOLD + bp + RESET)
        time.sleep(0.08)

    time.sleep(0.4)

    tagline = "— The Classic Game of Strategy —"
    trow = piece_row + 3
    tcol = max(1, (cols - len(tagline)) // 2)
    print_at(trow, tcol, "")
    typewrite(tagline, delay=0.04, color=C_DIM)

    div = "─" * 44
    drow = trow + 2
    dcol = max(1, (cols - 44) // 2)
    print_at(drow, dcol, C_GOLD + DIM + div + RESET)

    time.sleep(0.3)
    prompt_row = drow + 2
    pcol = max(1, (cols - 28) // 2)
    print_at(prompt_row, pcol, "")

    for _ in range(6):
        print_at(prompt_row, pcol, C_GOLD + "  Press  Enter  to  Begin  " + RESET)
        time.sleep(0.4)
        print_at(prompt_row, pcol, " " * 28)
        time.sleep(0.3)

    print_at(prompt_row, pcol, C_GOLD + "  Press  Enter  to  Begin  " + RESET)
    print_at(prompt_row + 2, 1, "")
    show_cursor()
    input()

# ═══════════════════════════════════════════════════════════════════════════════
#  FIREWORKS ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════
class Particle:
    def __init__(self, x, y, vx, vy, color, char, lifetime):
        self.x  = x;  self.y  = y
        self.vx = vx; self.vy = vy
        self.color    = color
        self.char     = char
        self.lifetime = lifetime
        self.age      = 0
        self.px = x;  self.py = y

    def update(self):
        self.px, self.py = self.x, self.y
        self.x  += self.vx
        self.y  += self.vy * 0.5
        self.vy += 0.25
        self.vx *= 0.96
        self.age += 1

    def alive(self):
        return self.age < self.lifetime

    def brightness(self):
        ratio = 1 - self.age / self.lifetime
        if ratio > 0.7:   return BOLD
        elif ratio > 0.4: return ""
        else:             return DIM

def launch_firework(cx, cy, rows, cols):
    particles = []
    count = random.randint(20, 32)
    color = random.choice(FIREWORK_COLORS)
    color2 = random.choice(FIREWORK_COLORS)
    for i in range(count):
        angle = 2 * math.pi * i / count + random.uniform(-0.2, 0.2)
        speed = random.uniform(1.2, 3.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        ch = random.choice(SPARKS)
        life = random.randint(8, 14)
        c = color if i % 2 == 0 else color2
        particles.append(Particle(cx, cy, vx, vy, c, ch, life))
    return particles

def winner_animation(winner_name):
    if SKIP_ANIMATIONS:
        show_cursor()
        print(f"\n{winner_name} wins by checkmate.")
        return
    hide_cursor()
    rows, cols = get_terminal_size()

    for color in [C_YELLOW, C_WHITE, C_GOLD, ""]:
        clear()
        if color:
            for r in range(rows):
                print(color + " " * cols + RESET)
        time.sleep(0.06)

    clear()

    all_particles = []
    launch_positions = [
        (cols // 4,     rows // 4),
        (3 * cols // 4, rows // 4),
        (cols // 2,     rows // 5),
        (cols // 3,     rows // 3),
        (2 * cols // 3, rows // 3),
    ]
    launch_times = [0, 4, 8, 12, 16]
    frame = 0
    total_frames = 45

    while frame < total_frames:
        for i, lt in enumerate(launch_times):
            if frame == lt and i < len(launch_positions):
                cx, cy = launch_positions[i]
                all_particles.extend(launch_firework(cx, cy, rows, cols))

        if frame > 10 and frame % 7 == 0:
            cx = random.randint(cols // 6, 5 * cols // 6)
            cy = random.randint(rows // 6, rows // 2)
            all_particles.extend(launch_firework(cx, cy, rows, cols))

        for p in all_particles:
            px, py = int(round(p.px)), int(round(p.py))
            if 1 <= py <= rows and 1 <= px <= cols:
                print_at(py, px, " ")

        new_particles = []
        for p in all_particles:
            p.update()
            if p.alive():
                px, py = int(round(p.x)), int(round(p.y))
                if 1 <= py <= rows - 4 and 1 <= px <= cols:
                    print_at(py, px, p.brightness() + p.color + p.char + RESET)
                new_particles.append(p)

        all_particles = new_particles

        if frame >= 6:
            _draw_winner_text(rows, cols, winner_name, frame)

        sys.stdout.flush()
        time.sleep(0.07)
        frame += 1

    clear()
    _draw_winner_text(rows, cols, winner_name, 99)
    print_at(rows - 2, 1, "")
    show_cursor()
    input(C_DIM + "\n  Press Enter to exit..." + RESET)

def _draw_winner_text(rows, cols, winner_name, frame):
    checkmate_art = [
        "  ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███╗   ███╗ █████╗ ████████╗███████╗  ",
        " ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝████╗ ████║██╔══██╗╚══██╔══╝██╔════╝  ",
        " ██║     ███████║█████╗  ██║     █████╔╝ ██╔████╔██║███████║   ██║   █████╗    ",
        " ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██║╚██╔╝██║██╔══██║   ██║   ██╔══╝    ",
        " ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗██║ ╚═╝ ██║██║  ██║   ██║   ███████╗  ",
        "  ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝  ",
    ]
    art_w     = max(len(l) for l in checkmate_art)
    start_col = max(1, (cols - art_w) // 2)
    mid_row   = rows // 2 - 5
    golds = [
        "\033[38;2;212;175;55m",
        "\033[38;2;240;200;80m",
        "\033[38;2;255;230;120m",
        "\033[38;2;200;160;40m",
    ]
    g = golds[frame % len(golds)]
    for i, line in enumerate(checkmate_art):
        print_at(mid_row + i, start_col, g + BOLD + line + RESET)
    win_text = f"♚  {winner_name.upper()} WINS  ♔"
    wt_col   = max(1, (cols - len(win_text)) // 2)
    print_at(mid_row + len(checkmate_art) + 2, wt_col, C_WHITE + BOLD + win_text + RESET)
    sep = "·  " * 14
    sc  = max(1, (cols - len(sep)) // 2)
    print_at(mid_row + len(checkmate_art) + 4, sc, C_GOLD + DIM + sep + RESET)

# ═══════════════════════════════════════════════════════════════════════════════
#  STALEMATE ANIMATION
# ═══════════════════════════════════════════════════════════════════════════════
def stalemate_animation():
    if SKIP_ANIMATIONS:
        show_cursor()
        print("\nDraw by stalemate.")
        return
    hide_cursor()
    rows, cols = get_terminal_size()
    clear()

    sub  = "The game is a draw"
    art = [
        " _____ _        _                     _       ",
        "/  ___| |      | |                   | |      ",
        r"\\ `--. | |_ __ | | ___ _ __ ___   __ _| |_ ___",
        r" `--. \| __/ _` | |/ _ \ '_ ` _ \ / _` | __/ _ |",
        r"/\__/ / || (_| | |  __/ | | | | | (_| | ||  __/",
        r"\____/ \__\__,_|_|\___|_| |_| |_|\__,_|\__\___|",
    ]

    for frame in range(40):
        offset  = max(0, 10 - frame)
        mid_row = rows // 2 - 5
        for i, line in enumerate(art):
            sc    = max(1, (cols - len(line)) // 2)
            alpha = min(1.0, (frame - i * 1.5) / 8)
            if alpha <= 0:   continue
            elif alpha < 0.4: color = C_DIM
            elif alpha < 0.8: color = "\033[38;2;150;150;150m"
            else:             color = "\033[38;2;200;200;200m" + BOLD
            print_at(mid_row + i - offset, sc, color + line + RESET)

        if frame > 15:
            pc = max(1, (cols - 5) // 2)
            if (frame // 4) % 2 == 0:
                print_at(mid_row + len(art) + 2, pc,
                         C_WHITE + BOLD + "♔" + RESET + "  " + TXT_BLACK_PIECE + BOLD + "♚" + RESET)
            else:
                print_at(mid_row + len(art) + 2, pc,
                         C_DIM   + BOLD + "♔" + RESET + "  " + C_DIM + BOLD + "♚" + RESET)
        if frame > 20:
            sc2 = max(1, (cols - len(sub)) // 2)
            print_at(mid_row + len(art) + 4, sc2, C_DIM + sub + RESET)

        sys.stdout.flush()
        time.sleep(0.07)

    print_at(rows - 2, 1, "")
    show_cursor()
    input(C_DIM + "\n  Press Enter to exit..." + RESET)

# ═══════════════════════════════════════════════════════════════════════════════
#  BOARD / GAME LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def initBoard():
    global en_passant_target
    castling_rights.update({"K": True, "Q": True, "k": True, "q": True})
    en_passant_target = None
    back = [2,3,4,5,6,4,3,2]
    for i in range(SIZE):
        for j in range(SIZE):
            if   i == 0: board[i][j] = -back[j]
            elif i == 1: board[i][j] = -1
            elif i == 6: board[i][j] =  1
            elif i == 7: board[i][j] =  back[j]
            else:         board[i][j] =  0

def copyBoard(src):
    return [row[:] for row in src]

def getPieceSymbol(p):
    if p > 0: return WHITE_SYMBOLS.get(p, " ")
    if p < 0: return BLACK_SYMBOLS.get(-p, " ")
    return " "

# ─── Larger board renderer ─────────────────────────────────────────────────────
def printBoard(selected=None, valid_moves=None, last_from=None, last_to=None, in_check_king=None):
    valid_set   = set((r2, c2) for _, _, r2, c2 in (valid_moves or []))
    capture_set = set()
    if valid_moves:
        for _, _, r2, c2 in valid_moves:
            if board[r2][c2] != 0:
                capture_set.add((r2, c2))

    _, cols = get_terminal_size()

    board_w = SIZE * SQ_W
    label_w = 4          # " 8  " rank label
    total_w = label_w + board_w + 2
    pad     = max(0, (cols - total_w) // 2)
    P       = " " * pad

    # File labels — each centred in SQ_W chars
    def file_label_row():
        return P + " " * label_w + "".join(f"{c:^{SQ_W}}" for c in "ABCDEFGH")

    top_rule = "─" * board_w

    print()
    print(C_GOLD + DIM + file_label_row() + RESET)
    print(P + C_GOLD + DIM + " " * label_w + f"╔{top_rule}╗" + RESET)

    for i in range(SIZE):
        rank = str(8 - i)

        # Build the SQ_H lines for this rank
        for line_idx in range(SQ_H):
            mid_line = (SQ_H // 2)  # centre line gets the piece

            if line_idx == mid_line:
                left_label  = C_GOLD + DIM + f" {rank:<2} ║" + RESET
                right_label = C_GOLD + DIM + f"║ {rank}" + RESET
            else:
                left_label  = C_GOLD + DIM + "    ║" + RESET
                right_label = C_GOLD + DIM + "║" + RESET

            row_str = P + left_label

            for j in range(SIZE):
                sq = (i, j)
                p  = board[i][j]

                # Choose background
                if selected and sq == (selected[0], selected[1]):
                    bg = BG_SELECTED
                elif sq in capture_set:
                    bg = BG_CAPTURE
                elif sq in valid_set:
                    bg = BG_VALID
                elif last_from and sq == (last_from[0], last_from[1]):
                    bg = BG_LASTMOVE
                elif last_to and sq == (last_to[0], last_to[1]):
                    bg = BG_LASTMOVE
                elif in_check_king and sq == (in_check_king[0], in_check_king[1]):
                    bg = BG_CHECK
                elif (i + j) % 2 == 0:
                    bg = BG_LIGHT
                else:
                    bg = BG_DARK

                if line_idx == mid_line:
                    # Centre line: show piece symbol centred in SQ_W chars
                    piece = getPieceSymbol(p)
                    txt = TXT_WHITE_PIECE if p > 0 else (TXT_BLACK_PIECE if p < 0 else "")
                    # pad symmetrically: half on each side
                    side = (SQ_W - 1) // 2   # chars of padding either side of 1-char piece
                    cell = bg + txt + " " * side + piece + " " * side + RESET
                else:
                    # Blank filler line
                    cell = bg + " " * SQ_W + RESET

                row_str += cell

            row_str += right_label
            print(row_str)

    print(P + C_GOLD + DIM + " " * label_w + f"╚{top_rule}╝" + RESET)
    print(C_GOLD + DIM + file_label_row() + RESET)
    print()

# ─── Move validation ────────────────────────────────────────────────────────────
def isPathClear(r1, c1, r2, c2, b):
    dr = (r2 > r1) - (r2 < r1)
    dc = (c2 > c1) - (c2 < c1)
    r, c = r1 + dr, c1 + dc
    while r != r2 or c != c2:
        if b[r][c] != 0: return False
        r += dr; c += dc
    return True

def isValidMove(r1, c1, r2, c2, turn, b):
    if not all(0 <= value < SIZE for value in (r1, c1, r2, c2)):
        return False
    if (r1, c1) == (r2, c2):
        return False
    p = b[r1][c1]; t = b[r2][c2]
    if p == 0 or p * turn < 0 or t * turn > 0 or abs(t) == 6: return False
    dr, dc = r2 - r1, c2 - c1
    ar, ac = abs(dr), abs(dc)
    piece  = abs(p)

    if piece == 1:
        dir = -1 if p > 0 else 1
        if dc == 0 and dr == dir     and t == 0: return True
        if dc == 0 and dr == 2 * dir and t == 0:
            if (p > 0 and r1 == 6) or (p < 0 and r1 == 1):
                return isPathClear(r1, c1, r2, c2, b)
        if ac == 1 and dr == dir and t != 0: return True
        if ac == 1 and dr == dir and t == 0 and (r2, c2) == en_passant_target:
            return b[r1][c2] == -turn
        return False
    elif piece == 2: return (dr == 0 or dc == 0) and isPathClear(r1, c1, r2, c2, b)
    elif piece == 3: return (ar == 2 and ac == 1) or (ar == 1 and ac == 2)
    elif piece == 4: return ar == ac and isPathClear(r1, c1, r2, c2, b)
    elif piece == 5: return ((dr == 0 or dc == 0) or ar == ac) and isPathClear(r1, c1, r2, c2, b)
    elif piece == 6:
        if ar <= 1 and ac <= 1: return True
        if dr != 0 or ac != 2 or r1 != (7 if turn == 1 else 0) or c1 != 4:
            return False
        side = "K" if turn == 1 else "k"
        if c2 == 2:
            side = "Q" if turn == 1 else "q"
            rook_col, between = 0, (1, 2, 3)
        elif c2 == 6:
            rook_col, between = 7, (5, 6)
        else:
            return False
        if not castling_rights[side] or b[r1][rook_col] != 2 * turn:
            return False
        if any(b[r1][col] != 0 for col in between) or isKingInCheck(turn, b):
            return False
        transit = copyBoard(b)
        transit[r1][4] = 0
        transit[r1][5 if c2 == 6 else 3] = 6 * turn
        return not isKingInCheck(turn, transit)
    return False

def makeMove(r1, c1, r2, c2, b, update_state=False):
    global en_passant_target
    piece = b[r1][c1]
    captured_piece = b[r2][c2]
    previous_target = en_passant_target
    is_en_passant = (
        abs(piece) == 1 and c1 != c2 and b[r2][c2] == 0
        and (r2, c2) == previous_target
    )
    is_castling = abs(piece) == 6 and abs(c2 - c1) == 2
    b[r2][c2] = piece
    b[r1][c1] = 0
    if is_en_passant:
        b[r1][c2] = 0
    if is_castling:
        rook_from, rook_to = (7, 5) if c2 == 6 else (0, 3)
        b[r1][rook_to] = b[r1][rook_from]
        b[r1][rook_from] = 0
    if update_state:
        if abs(piece) == 6:
            castling_rights["K" if piece > 0 else "k"] = False
            castling_rights["Q" if piece > 0 else "q"] = False
        if abs(piece) == 2:
            if (r1, c1) == (7, 0): castling_rights["Q"] = False
            if (r1, c1) == (7, 7): castling_rights["K"] = False
            if (r1, c1) == (0, 0): castling_rights["q"] = False
            if (r1, c1) == (0, 7): castling_rights["k"] = False
        captured_square = (r1, c2) if is_en_passant else (r2, c2)
        if abs(captured_piece) == 2:
            if captured_square == (7, 0): castling_rights["Q"] = False
            if captured_square == (7, 7): castling_rights["K"] = False
            if captured_square == (0, 0): castling_rights["q"] = False
            if captured_square == (0, 7): castling_rights["k"] = False
        en_passant_target = ((r1 + r2) // 2, c1) if abs(piece) == 1 and abs(r2 - r1) == 2 else None

def getValidMoves(r1, c1, turn, b):
    moves = []
    for r2 in range(SIZE):
        for c2 in range(SIZE):
            if isValidMove(r1, c1, r2, c2, turn, b):
                temp = copyBoard(b)
                makeMove(r1, c1, r2, c2, temp)
                if not isKingInCheck(turn, temp):
                    moves.append((r1, c1, r2, c2))
    return moves

def isKingInCheck(turn, b):
    king = findKingPos(turn, b)
    if king is None:
        return True
    king_r, king_c = king
    for r in range(SIZE):
        for c in range(SIZE):
            piece = b[r][c]
            if piece * turn >= 0:
                continue
            dr, dc = king_r - r, king_c - c
            ar, ac = abs(dr), abs(dc)
            kind = abs(piece)
            if kind == 1 and dr == (1 if piece < 0 else -1) and ac == 1:
                return True
            if kind == 3 and (ar, ac) in ((2, 1), (1, 2)):
                return True
            if kind == 6 and max(ar, ac) == 1:
                return True
            if kind == 2 and (dr == 0 or dc == 0) and isPathClear(r, c, king_r, king_c, b):
                return True
            if kind == 4 and ar == ac and isPathClear(r, c, king_r, king_c, b):
                return True
            if kind == 5 and (dr == 0 or dc == 0 or ar == ac) and isPathClear(r, c, king_r, king_c, b):
                return True
    return False

def findKingPos(turn, b):
    kingVal = 6 if turn == 1 else -6
    for i in range(SIZE):
        for j in range(SIZE):
            if b[i][j] == kingVal: return (i, j)
    return None

def isCheckmate(turn):
    if not isKingInCheck(turn, board): return False
    for r1 in range(SIZE):
        for c1 in range(SIZE):
            if (turn == 1 and board[r1][c1] > 0) or (turn == -1 and board[r1][c1] < 0):
                if getValidMoves(r1, c1, turn, board): return False
    return True

def isStalemate(turn):
    if isKingInCheck(turn, board): return False
    for r1 in range(SIZE):
        for c1 in range(SIZE):
            if (turn == 1 and board[r1][c1] > 0) or (turn == -1 and board[r1][c1] < 0):
                if getValidMoves(r1, c1, turn, board): return False
    return True

# ─── Input parsing ─────────────────────────────────────────────────────────────
def parseInput(move):
    match = re.fullmatch(r"([a-h][1-8])(?:([a-h][1-8]))?", move.strip(), re.IGNORECASE)
    if match is None:
        return None
    start, destination = match.groups()
    r1, c1 = 8 - int(start[1]), ord(start[0].lower()) - ord("a")
    if destination is None:
        return r1, c1, None, None
    r2, c2 = 8 - int(destination[1]), ord(destination[0].lower()) - ord("a")
    return r1, c1, r2, c2

# ─── Pawn promotion ────────────────────────────────────────────────────────────
def promotePawn(r, c, turn):
    opts = {"q": 5, "r": 2, "b": 4, "n": 3}
    while True:
        choice = input(
            C_GOLD + "  Promote pawn → " + RESET +
            "[q]ueen  [r]ook  [b]ishop  [n]ight: "
        ).strip().lower()
        if choice in opts:
            board[r][c] = opts[choice] * turn
            return

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def statusBar(turn, in_check):
    player  = C_WHITE + BOLD + "WHITE ♔" + RESET if turn == 1 else TXT_BLACK_PIECE + BOLD + "BLACK ♚" + RESET
    check_w = "  " + C_RED + BOLD + "⚠  KING IN CHECK!" + RESET if in_check else ""
    print(f"  {player}'s turn{check_w}")

def printCaptured(captured_w, captured_b):
    _, cols = get_terminal_size()
    pad = " " * max(0, (cols - 60) // 2)

    def fmt_white(pieces):
        return TXT_BLACK_PIECE + "  ".join(BLACK_SYMBOLS.get(abs(p), "?") for p in sorted(pieces, key=lambda x: -abs(x))) + RESET

    def fmt_black(pieces):
        return TXT_WHITE_PIECE + "  ".join(WHITE_SYMBOLS.get(abs(p), "?") for p in sorted(pieces, key=lambda x: -abs(x))) + RESET

    if captured_w:
        print(pad + C_DIM + "  White captured: " + RESET + fmt_white(captured_w))
    if captured_b:
        print(pad + C_DIM + "  Black captured: " + RESET + fmt_black(captured_b))
    if captured_w or captured_b:
        print()

def main():
    fade_in_title()

    turn        = 1
    selected_sq = None
    valid_moves = []
    last_from   = None
    last_to     = None
    captured_w  = []
    captured_b  = []

    initBoard()

    while True:
        clear()

        in_check = isKingInCheck(turn, board)
        king_pos = findKingPos(turn, board) if in_check else None

        printBoard(
            selected      = selected_sq,
            valid_moves   = valid_moves,
            last_from     = last_from,
            last_to       = last_to,
            in_check_king = king_pos,
        )

        printCaptured(captured_w, captured_b)
        statusBar(turn, in_check)

        if isCheckmate(turn):
            winner = "White" if turn == -1 else "Black"
            print(C_RED + BOLD + f"\n  ✦ CHECKMATE — {winner.upper()} WINS ✦\n" + RESET)
            time.sleep(1.5)
            winner_animation(winner)
            break

        if isStalemate(turn):
            print(C_YELLOW + BOLD + "\n  ✦ STALEMATE — IT'S A DRAW ✦\n" + RESET)
            time.sleep(1.5)
            stalemate_animation()
            break

        hint = (
            C_DIM + "  (select: e2 · move: e2e4 · deselect: same square · quit: q)" + RESET
            if not selected_sq else
            C_GOLD + f"  ✦ {chr(ord('a')+selected_sq[1]).upper()}{8-selected_sq[0]} selected — enter destination (or same to deselect)" + RESET
        )
        print(hint)

        move_str = input(C_DIM + "\n  › " + RESET).strip()

        if move_str.lower() == 'q':
            print(C_DIM + "\n  Goodbye.\n" + RESET)
            break

        parsed = parseInput(move_str)

        if not parsed:
            input(C_RED + "  ✗ Invalid format. Press Enter…" + RESET)
            continue

        r1, c1, r2, c2 = parsed

        if r2 is None:
            if (turn == 1 and board[r1][c1] > 0) or (turn == -1 and board[r1][c1] < 0):
                if selected_sq and selected_sq == (r1, c1):
                    selected_sq = None; valid_moves = []
                else:
                    selected_sq = (r1, c1)
                    valid_moves = getValidMoves(r1, c1, turn, board)
            else:
                input(C_RED + "  ✗ No friendly piece there. Press Enter…" + RESET)
            continue

        if selected_sq is None:
            if (turn == 1 and board[r1][c1] > 0) or (turn == -1 and board[r1][c1] < 0):
                selected_sq = (r1, c1)
                valid_moves = getValidMoves(r1, c1, turn, board)
            else:
                input(C_RED + "  ✗ No friendly piece there. Press Enter…" + RESET)
            continue

        sr, sc = selected_sq

        if (r1, c1) != (sr, sc):
            if (turn == 1 and board[r1][c1] > 0) or (turn == -1 and board[r1][c1] < 0):
                selected_sq = (r1, c1)
                valid_moves = getValidMoves(r1, c1, turn, board)
                continue
            r2, c2 = r1, c1
            r1, c1 = sr, sc

        if not isValidMove(r1, c1, r2, c2, turn, board):
            input(C_RED + "  ✗ Invalid move. Press Enter…" + RESET)
            continue

        temp = copyBoard(board)
        makeMove(r1, c1, r2, c2, temp)
        if isKingInCheck(turn, temp):
            input(C_RED + "  ✗ That move leaves your king in check! Press Enter…" + RESET)
            continue

        captured = board[r2][c2]
        if abs(board[r1][c1]) == 1 and c1 != c2 and captured == 0:
            captured = board[r1][c2]
        makeMove(r1, c1, r2, c2, board, update_state=True)

        if captured != 0:
            if turn == 1: captured_w.append(captured)
            else:         captured_b.append(captured)

        if abs(board[r2][c2]) == 1 and (r2 == 0 or r2 == 7):
            promotePawn(r2, c2, turn)

        last_from   = (r1, c1)
        last_to     = (r2, c2)
        selected_sq = None
        valid_moves = []
        turn        = -turn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a two-player chess game in your terminal.")
    parser.add_argument("--no-animation", action="store_true", help="skip the animated title and end screens")
    SKIP_ANIMATIONS = parser.parse_args().no_animation
    main()


