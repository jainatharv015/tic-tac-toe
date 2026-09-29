"""
Tic Tac Toe - single file version (Python + tkinter)
Run with:  python tic_tac_toe.py
Modes: 2 Players or vs Computer (Easy / Medium / Hard)
"""
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- colours and sizes ----------------
BG, PANEL, GRID = "#141726", "#1f2340", "#3b4272"
X_COLOR, O_COLOR, WIN_COLOR = "#ff5c8a", "#33d6ff", "#ffd93d"
TEXT, MUTED = "#f2f4ff", "#8b90b8"
CELL, PAD = 120, 15
BOARD_SIZE = CELL * 3 + PAD * 2
SCORE_FILE = "scores.json"

# all 8 ways to win (rows, columns, diagonals)
WIN_LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
             (0, 3, 6), (1, 4, 7), (2, 5, 8),
             (0, 4, 8), (2, 4, 6)]


# ================= GAME LOGIC =================
class Board:
    """The 3x3 board. Cells are numbered 0-8, left to right, top to bottom."""

    def __init__(self):
        self.cells = [" "] * 9

    def make_move(self, index, symbol):
        if symbol not in ("X", "O"):
            raise ValueError("Symbol must be X or O")
        if not (0 <= index <= 8) or self.cells[index] != " ":
            raise ValueError("Invalid move")
        self.cells[index] = symbol

    def winning_line(self):
        for a, b, c in WIN_LINES:
            if self.cells[a] != " " and self.cells[a] == self.cells[b] == self.cells[c]:
                return (a, b, c)
        return None

    def get_winner(self):
        line = self.winning_line()
        return self.cells[line[0]] if line else None

    def is_full(self):
        return " " not in self.cells

    def available_moves(self):
        return [i for i, c in enumerate(self.cells) if c == " "]

    def reset(self):
        self.cells = [" "] * 9


# ================= COMPUTER PLAYER =================
def easy_move(board):
    """Easy: random empty cell."""
    return random.choice(board.available_moves())


def find_winning_move(board, symbol):
    """Return a cell where `symbol` would win right now (or None)."""
    for move in board.available_moves():
        board.cells[move] = symbol           # try it
        won = board.get_winner() == symbol
        board.cells[move] = " "              # undo it
        if won:
            return move
    return None


def medium_move(board):
    """Medium: win if possible, else block X, else random."""
    move = find_winning_move(board, "O")
    if move is None:
        move = find_winning_move(board, "X")
    if move is None:
        move = easy_move(board)
    return move


def minimax(board, depth, is_computer_turn):
    """Score a position: positive = good for computer (O), negative = good for X."""
    winner = board.get_winner()
    if winner == "O":
        return 10 - depth
    if winner == "X":
        return depth - 10
    if board.is_full():
        return 0
    scores = []
    for move in board.available_moves():
        board.cells[move] = "O" if is_computer_turn else "X"
        scores.append(minimax(board, depth + 1, not is_computer_turn))
        board.cells[move] = " "
    return max(scores) if is_computer_turn else min(scores)


def hard_move(board):
    """Hard: Minimax - the computer never loses."""
    best_score, best_move = -100, None
    for move in board.available_moves():
        board.cells[move] = "O"
        score = minimax(board, 1, False)
        board.cells[move] = " "
        if score > best_score:
            best_score, best_move = score, move
    return best_move


def get_computer_move(board, level):
    if level == "Easy":
        return easy_move(board)
    if level == "Medium":
        return medium_move(board)
    return hard_move(board)


# ================= SCORES (saved in a file) =================
def load_scores():
    try:
        with open(SCORE_FILE) as f:
            data = json.load(f)
        return {k: int(data.get(k, 0)) for k in ("X", "O", "Draw")}
    except (FileNotFoundError, ValueError, AttributeError):
        return {"X": 0, "O": 0, "Draw": 0}


def save_scores(scores):
    try:
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f)
    except OSError:
        pass                                  # not being able to save is not fatal


# ================= GRAPHICS =================
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.board = Board()
        self.scores = load_scores()
        self.current = "X"
        self.game_over = False
        self.mode = tk.StringVar(value="Computer")
        self.level = tk.StringVar(value="Hard")

        root.title("Tic Tac Toe")
        root.configure(bg=BG)
        root.resizable(False, False)
        self.build_window()
        self.new_round()

    def build_window(self):
        tk.Label(self.root, text="TIC  TAC  TOE", font=("Segoe UI", 24, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(15, 5))

        # score cards
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=5)
        self.score_labels = {}
        for key, name, color in (("X", "Player X", X_COLOR), ("Draw", "Draws", MUTED),
                                 ("O", "Player O", O_COLOR)):
            card = tk.Frame(frame, bg=PANEL, padx=18, pady=6)
            card.pack(side="left", padx=6)
            tk.Label(card, text=name, font=("Segoe UI", 10), bg=PANEL, fg=color).pack()
            label = tk.Label(card, text="0", font=("Segoe UI", 20, "bold"), bg=PANEL, fg=TEXT)
            label.pack()
            self.score_labels[key] = label

        # mode and level
        options = tk.Frame(self.root, bg=BG)
        options.pack(pady=8)
        tk.Label(options, text="Mode:", bg=BG, fg=MUTED).pack(side="left")
        mode_box = ttk.Combobox(options, textvariable=self.mode, width=10,
                                state="readonly", values=["Computer", "2 Players"])
        mode_box.pack(side="left", padx=5)
        tk.Label(options, text="Level:", bg=BG, fg=MUTED).pack(side="left")
        self.level_box = ttk.Combobox(options, textvariable=self.level, width=8,
                                      state="readonly", values=["Easy", "Medium", "Hard"])
        self.level_box.pack(side="left", padx=5)
        mode_box.bind("<<ComboboxSelected>>", lambda e: self.new_round())
        self.level_box.bind("<<ComboboxSelected>>", lambda e: self.new_round())

        self.status = tk.Label(self.root, text="", font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXT)
        self.status.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE, height=BOARD_SIZE,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(padx=20)
        self.canvas.bind("<Button-1>", self.on_click)

        buttons = tk.Frame(self.root, bg=BG)
        buttons.pack(pady=15)
        tk.Button(buttons, text="New Round", width=12, command=self.new_round,
                  bg=O_COLOR, fg=BG, relief="flat").pack(side="left", padx=6)
        tk.Button(buttons, text="Reset Scores", width=12, command=self.reset_scores,
                  bg=PANEL, fg=TEXT, relief="flat").pack(side="left", padx=6)

    # ----- drawing -----
    def cell_center(self, index):
        row, col = divmod(index, 3)
        return PAD + col * CELL + CELL // 2, PAD + row * CELL + CELL // 2

    def draw_board(self):
        self.canvas.delete("all")
        for i in (1, 2):                                   # grid lines
            self.canvas.create_line(PAD + i * CELL, PAD + 10, PAD + i * CELL, PAD + 3 * CELL - 10,
                                    fill=GRID, width=5, capstyle="round")
            self.canvas.create_line(PAD + 10, PAD + i * CELL, PAD + 3 * CELL - 10, PAD + i * CELL,
                                    fill=GRID, width=5, capstyle="round")
        for index, symbol in enumerate(self.board.cells):  # X and O
            x, y = self.cell_center(index)
            if symbol == "X":
                d = 32
                self.canvas.create_line(x - d, y - d, x + d, y + d, fill=X_COLOR,
                                        width=10, capstyle="round")
                self.canvas.create_line(x - d, y + d, x + d, y - d, fill=X_COLOR,
                                        width=10, capstyle="round")
            elif symbol == "O":
                r = 36
                self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=O_COLOR, width=10)
        line = self.board.winning_line()                   # winning line
        if line:
            x1, y1 = self.cell_center(line[0])
            x2, y2 = self.cell_center(line[2])
            self.canvas.create_line(x1, y1, x2, y2, fill=WIN_COLOR, width=8, capstyle="round")

    def update_scores(self):
        for key, label in self.score_labels.items():
            label.config(text=str(self.scores[key]))

    def set_status(self, text, color=TEXT):
        self.status.config(text=text, fg=color)

    def show_turn(self):
        if self.mode.get() == "Computer":
            self.set_status("Your turn (X)", X_COLOR)
        else:
            self.set_status(f"Player {self.current}'s turn",
                            X_COLOR if self.current == "X" else O_COLOR)

    # ----- game flow -----
    def new_round(self):
        self.board.reset()
        self.current = "X"
        self.game_over = False
        self.draw_board()
        self.update_scores()
        self.level_box.config(state="readonly" if self.mode.get() == "Computer" else "disabled")
        self.show_turn()

    def on_click(self, event):
        if self.game_over or (self.mode.get() == "Computer" and self.current == "O"):
            return
        col = (event.x - PAD) // CELL
        row = (event.y - PAD) // CELL
        if 0 <= col < 3 and 0 <= row < 3:
            self.play(row * 3 + col)

    def play(self, index):
        try:
            self.board.make_move(index, self.current)
        except ValueError:
            self.set_status("That square is taken!", WIN_COLOR)
            return
        self.draw_board()
        if self.check_end():
            return
        self.current = "O" if self.current == "X" else "X"
        if self.mode.get() == "Computer" and self.current == "O":
            self.set_status("Computer is thinking...", O_COLOR)
            self.root.after(500, self.computer_turn)
        else:
            self.show_turn()

    def computer_turn(self):
        if not self.game_over and self.board.available_moves():
            self.play(get_computer_move(self.board, self.level.get()))

    def check_end(self):
        winner = self.board.get_winner()
        if winner:
            self.finish(winner)
            if self.mode.get() == "Computer":
                self.set_status("You win!" if winner == "X" else "Computer wins!", WIN_COLOR)
            else:
                self.set_status(f"Player {winner} wins!", WIN_COLOR)
            return True
        if self.board.is_full():
            self.finish("Draw")
            self.set_status("It's a draw!", MUTED)
            return True
        return False

    def finish(self, result):
        self.game_over = True
        self.scores[result] += 1
        save_scores(self.scores)
        self.update_scores()

    def reset_scores(self):
        if messagebox.askyesno("Reset scores", "Set all scores back to 0?"):
            self.scores = {"X": 0, "O": 0, "Draw": 0}
            save_scores(self.scores)
            self.update_scores()


if __name__ == "__main__":
    window = tk.Tk()
    TicTacToeApp(window)
    window.mainloop()
