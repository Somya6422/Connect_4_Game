import tkinter as tk
from tkinter import messagebox
import json
import os
import random

ROWS = 6
COLS = 7
CELL = 90

SAVE_FILE = "connect4_save.json"
STATS_FILE = "connect4_stats.json"

class ConnectFour:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four Pro")
        self.root.configure(bg="#0f172a")
        self.root.geometry("680x720")
        self.root.resizable(False, False)
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.current_player = 1
        self.animating = False
        self.game_over = False
        self.game_mode = "PvP"
        self.ai_difficulty = "Medium"
        self.move_history = []
        self.stats = self.load_stats()
        self.start_frame = tk.Frame(self.root, bg="#0f172a")
        self.game_frame = tk.Frame(self.root, bg="#0f172a")
        self.setup_start_screen()
        self.setup_game_screen()
        self.start_frame.pack(expand=True, fill="both")

    def setup_start_screen(self):
        inner_frame = tk.Frame(self.start_frame, bg="#0f172a")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            inner_frame, text="CONNECT FOUR PRO",
            font=("Segoe UI", 32, "bold"),
            bg="#0f172a", fg="#38bdf8"
        ).pack(pady=30)

        tk.Button(
            inner_frame, text="🤖 1 Player (Vs AI)",
            font=("Segoe UI", 16, "bold"),
            bg="#3b82f6", fg="white",
            activebackground="#2563eb", activeforeground="white",
            width=18, pady=8, bd=0, cursor="hand2",
            command=self.show_difficulty_dialog
        ).pack(pady=10)

        tk.Button(
            inner_frame, text="👥 2 Players (Local)",
            font=("Segoe UI", 16, "bold"),
            bg="#10b981", fg="white",
            activebackground="#059669", activeforeground="white",
            width=18, pady=8, bd=0, cursor="hand2",
            command=lambda: self.start_game("PvP")
        ).pack(pady=10)

        tk.Button(
            inner_frame, text="🚪 Exit",
            font=("Segoe UI", 16, "bold"),
            bg="#ef4444", fg="white",
            activebackground="#dc2626", activeforeground="white",
            width=18, pady=8, bd=0, cursor="hand2",
            command=self.root.destroy
        ).pack(pady=10)

    def setup_game_screen(self):
        tk.Label(
            self.game_frame, text="CONNECT FOUR PRO",
            font=("Segoe UI", 20, "bold"),
            bg="#0f172a", fg="white"
        ).pack(pady=8)
        self.turn_label = tk.Label(
            self.game_frame, text="🔴 Red's Turn",
            font=("Segoe UI", 12, "bold"),
            bg="#0f172a", fg="white"
        )
        self.turn_label.pack()
        self.stats_label = tk.Label(
            self.game_frame,
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Segoe UI", 10)
        )
        self.stats_label.pack()
        self.update_stats_label()
        self.canvas = tk.Canvas(
            self.game_frame,
            width=COLS * CELL,
            height=ROWS * CELL,
            bg="#1565c0",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        btn_frame = tk.Frame(self.game_frame, bg="#0f172a")
        btn_frame.pack(pady=5)

        self.menu_btn = tk.Button(btn_frame, text="📋 Menu", width=7, bg="#94a3b8", fg="white", command=self.return_to_menu)
        self.menu_btn.grid(row=0, column=0, padx=4)

        self.save_btn = tk.Button(btn_frame, text="💾 Save", width=7, bg="#94a3b8", fg="white", command=self.save_game)
        self.save_btn.grid(row=0, column=1, padx=4)

        self.load_btn = tk.Button(btn_frame, text="📂 Load", width=7, bg="#94a3b8", fg="white", command=self.load_game)
        self.load_btn.grid(row=0, column=2, padx=4)

        self.undo_btn = tk.Button(btn_frame, text="↩️  Undo", width=7, bg="#94a3b8", fg="white", command=self.undo_move, state=tk.DISABLED)
        self.undo_btn.grid(row=0, column=3, padx=4)

        self.stats_btn = tk.Button(btn_frame, text="🏆 Stats", width=7, bg="#94a3b8", fg="white", command=self.show_stats)
        self.stats_btn.grid(row=0, column=4, padx=4)

        tk.Button(btn_frame, text="🚪 Exit", width=7, bg="#ef4444", fg="white", command=self.root.destroy).grid(row=0, column=5, padx=4)

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", self.clear_hover)

    def start_game(self, mode):
        self.game_mode = mode
        self.start_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        # Update undo button visibility based on game mode
        if self.game_mode == "PvP":
            self.undo_btn.config(state=tk.NORMAL)
        else:
            self.undo_btn.config(state=tk.DISABLED)
        self.new_game()

    def return_to_menu(self):
        self.game_frame.pack_forget()
        self.start_frame.pack(fill="both", expand=True)
        # Reset difficulty to Medium when returning to menu
        self.ai_difficulty = "Medium"

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    data = json.load(f)
                    required_keys = ["games", "red_wins", "yellow_wins", "draws"]
                    return {k: data.get(k, 0) for k in required_keys}
            except (json.JSONDecodeError, OSError, TypeError):
                pass
        return {"games": 0, "red_wins": 0, "yellow_wins": 0, "draws": 0}
    
    def get_win_percentage(self, player):
        """Calculate win percentage for a player (1=Red, 2=Yellow)."""
        if self.stats["games"] == 0:
            return 0.0
        wins = self.stats["red_wins"] if player == 1 else self.stats["yellow_wins"]
        return (wins / self.stats["games"]) * 100

    def save_stats(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f, indent=4)

    def update_stats_label(self):
        s = self.stats
        mode_text = f"Vs AI ({self.ai_difficulty})" if self.game_mode == "PvAI" else "Local PvP"
        red_pct = self.get_win_percentage(1)
        yellow_pct = self.get_win_percentage(2)
        self.stats_label.config(
            text=f"Mode: {mode_text} | Games: {s['games']} | Red: {s['red_wins']} ({red_pct:.1f}%) | Yellow: {s['yellow_wins']} ({yellow_pct:.1f}%) | Draws: {s['draws']}"
        )

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL + 8
                y1 = r * CELL + 8
                x2 = x1 + CELL - 16
                y2 = y1 + CELL - 16
                color = "#e2e8f0"
                if self.board[r][c] == 1:
                    color = "#ef4444"
                elif self.board[r][c] == 2:
                    color = "#facc15"
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")

    def hover(self, event):
        self.clear_hover()
        if self.game_over or self.animating or (self.game_mode == "PvAI" and self.current_player == 2):
            return
        col = event.x // CELL
        if not (0 <= col < COLS):
            return
        target_row = self.find_row(col)
        if target_row == -1:
            return
        color = "#ef4444" if self.current_player == 1 else "#facc15"
        x1 = col * CELL + 8
        y1 = target_row * CELL + 8
        x2 = x1 + CELL - 16
        y2 = y1 + CELL - 16
        self.canvas.create_oval(
            x1, y1, x2, y2, 
            outline=color, width=3, dash=(6, 4), tags="hover"
        )

    def clear_hover(self, event=None):
        self.canvas.delete("hover")

    def click(self, event):
        if self.game_over or self.animating or (self.game_mode == "PvAI" and self.current_player == 2):
            return
        col = event.x // CELL
        if not (0 <= col < COLS):
            return
        row = self.find_row(col)
        if row == -1:
            messagebox.showwarning("Full Column", "This column is full! Choose another.")
            return
        self.clear_hover()
        self.move_history.append((row, col, self.current_player))
        if len(self.move_history) >= 2:
            self.undo_btn.config(state=tk.NORMAL)
        self.animate_drop(row, col)

    def find_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return -1

    def animate_drop(self, target_row, col):
        self.animating = True
        color = "#ef4444" if self.current_player == 1 else "#facc15"
        x1 = col * CELL + 8
        x2 = x1 + CELL - 16
        piece = self.canvas.create_oval(
            x1, 8, x2, CELL - 8,
            fill=color, outline=""
        )
        target_y = target_row * CELL + 8

        def step():
            x1c, y1c, x2c, y2c = self.canvas.coords(piece)
            if y1c < target_y:
                self.canvas.move(piece, 0, 15)
                self.root.after(8, step)
            else:
                self.board[target_row][col] = self.current_player
                self.draw_board()
                self.animating = False
                self.after_move(target_row, col)
        step()

    def undo_move(self):
        """Undo the last move (PvP only)."""
        if self.game_mode != "PvP" or len(self.move_history) < 2 or self.game_over:
            messagebox.showinfo("Undo", "Cannot undo at this time.")
            return
        
        for _ in range(2):
            if self.move_history:
                row, col, player = self.move_history.pop()
                self.board[row][col] = 0
        self.current_player = 1 if len(self.move_history) % 2 == 0 else 2
        self.draw_board()
        turn_text = "🔴 Red's Turn" if self.current_player == 1 else "🟡 Yellow's Turn"
        self.turn_label.config(text=turn_text)
        self.undo_btn.config(state=tk.NORMAL if len(self.move_history) >= 2 else tk.DISABLED)
        messagebox.showinfo("Undo", "Last move undone.")

    def after_move(self, row, col):
        winning_cells = self.check_win(row, col)
        if winning_cells:
            self.game_over = True
            self.stats["games"] += 1
            self.highlight_win(winning_cells)
            self.root.update()
            winner = "Red" if self.current_player == 1 else "Yellow"
            if self.current_player == 1:
                self.stats["red_wins"] += 1
            else:
                self.stats["yellow_wins"] += 1
            self.save_stats()
            self.update_stats_label()
            messagebox.showinfo("Winner", f"{winner} wins!")
            self.new_game()
            return
        if self.board_full():
            self.game_over = True
            self.stats["games"] += 1
            self.stats["draws"] += 1
            self.save_stats()
            self.update_stats_label()
            self.root.update()
            messagebox.showinfo("Draw", "Match Draw!")
            self.new_game()
            return
        self.current_player = 2 if self.current_player == 1 else 1
        turn_text = "🔴 Red's Turn" if self.current_player == 1 else "🟡 Yellow's Turn"
        if self.game_mode == "PvAI" and self.current_player == 2:
            turn_text = "🟡 AI is thinking..."
        self.turn_label.config(text=turn_text)
        if self.game_mode == "PvAI" and self.current_player == 2:
            self.root.after(600, self.ai_move)

    def simulate_move(self, col, player):
        """Temporarily places a piece to check if it results in a win."""
        row = self.find_row(col)
        if row == -1:  # Column is full
            return None
        self.board[row][col] = player
        win = self.check_win(row, col)
        self.board[row][col] = 0  # Undo move
        return win

    def ai_move(self):
        if self.game_over:
            return
        valid_cols = [c for c in range(COLS) if self.board[0][c] == 0]
        if not valid_cols:
            return
        target_col = None
        if self.ai_difficulty == "Easy":
            if random.random() < 0.2:
                for col in valid_cols:
                    if self.simulate_move(col, 2):
                        target_col = col
                        break
                if target_col is None:
                    for col in valid_cols:
                        if self.simulate_move(col, 1):
                            target_col = col
                            break
            if target_col is None:
                target_col = random.choice(valid_cols)
        elif self.ai_difficulty == "Medium":
            for col in valid_cols:
                if self.simulate_move(col, 2):
                    target_col = col
                    break
            if target_col is None:
                for col in valid_cols:
                    if self.simulate_move(col, 1):
                        target_col = col
                        break
            if target_col is None and 3 in valid_cols and random.random() > 0.3:
                target_col = 3
            if target_col is None:
                target_col = random.choice(valid_cols)

        else:
            for col in valid_cols:
                if self.simulate_move(col, 2):
                    target_col = col
                    break
            if target_col is None:
                for col in valid_cols:
                    if self.simulate_move(col, 1):
                        target_col = col
                        break
            if target_col is None:
                center_cols = [c for c in valid_cols if c in [3, 2, 4]]
                if center_cols:
                    target_col = random.choice(center_cols)
            if target_col is None:
                target_col = random.choice(valid_cols)
        row = self.find_row(target_col)
        self.move_history.append((row, target_col, 2))
        self.animate_drop(row, target_col)

    def board_full(self):
        return all(0 not in row for row in self.board)

    def get_directional_cells(self, row, col, dr, dc):
        player = self.board[row][col]
        cells = [(row, col)]
        r, c = row + dr, col + dc
        while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
            cells.append((r, c))
            r += dr
            c += dc
        r, c = row - dr, col - dc
        while 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == player:
            cells.append((r, c))
            r -= dr
            c -= dc
        return cells

    def check_win(self, row, col):
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            cells = self.get_directional_cells(row, col, dr, dc)
            if len(cells) >= 4:
                return cells
        return None

    def highlight_win(self, cells):
        cells.sort()
        start_r, start_c = cells[0]
        end_r, end_c = cells[-1]
        x1 = start_c * CELL + CELL // 2
        y1 = start_r * CELL + CELL // 2
        x2 = end_c * CELL + CELL // 2
        y2 = end_r * CELL + CELL // 2
        self.canvas.create_line(
            x1, y1, x2, y2, 
            fill="#10b981", width=8, capstyle=tk.ROUND, tags="win_line"
        )

    def new_game(self):
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.current_player = 1
        self.game_over = False
        self.animating = False
        self.move_history = []
        self.turn_label.config(text="🔴 Red's Turn")
        if self.game_mode == "PvP":
            self.undo_btn.config(state=tk.DISABLED)
        self.update_stats_label()
        self.draw_board()

    def save_game(self):
        data = {
            "board": self.board,
            "player": self.current_player,
            "game_over": self.game_over,
            "mode": self.game_mode,
            "ai_difficulty": self.ai_difficulty
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Saved", "Game saved successfully.")

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            messagebox.showwarning("Load", "No save file found.")
            return
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)

            if "board" not in data or "player" not in data:
                messagebox.showerror("Load Error", "Save file is corrupted.")
                return
            self.board = data["board"]
            self.current_player = data["player"]
            self.game_over = data.get("game_over", False)
            self.game_mode = data.get("mode", "PvP")
            self.ai_difficulty = data.get("ai_difficulty", "Medium")
            self.move_history = []
            turn_text = "🔴 Red's Turn" if self.current_player == 1 else "🟡 Yellow's Turn"
            self.turn_label.config(text=turn_text)
            self.update_stats_label()
            self.draw_board()
            messagebox.showinfo("Loaded", "Game loaded successfully.")
            if self.game_mode == "PvAI" and self.current_player == 2 and not self.game_over:
                self.turn_label.config(text="🟡 AI is thinking...")
                self.root.after(500, self.ai_move)
        except (json.JSONDecodeError, IOError, TypeError) as e:
            messagebox.showerror("Load Error", f"Failed to load game: {str(e)}")

    def show_stats(self):
        s = self.stats
        red_pct = self.get_win_percentage(1)
        yellow_pct = self.get_win_percentage(2)
        draw_pct = (s['draws'] / s['games'] * 100) if s['games'] > 0 else 0
        messagebox.showinfo(
            "Statistics",
            f"Games Played: {s['games']}\n\n"
            f"Red Wins: {s['red_wins']} ({red_pct:.1f}%)\n"
            f"Yellow Wins: {s['yellow_wins']} ({yellow_pct:.1f}%)\n"
            f"Draws: {s['draws']} ({draw_pct:.1f}%)"
        )

    def show_difficulty_dialog(self):
        """Show difficulty selection dialog for AI mode."""
        dialog_window = tk.Toplevel(self.root)
        dialog_window.title("Select Difficulty")
        dialog_window.geometry("320x320")
        dialog_window.configure(bg="#0f172a")
        dialog_window.resizable(False, False)
        dialog_window.transient(self.root)
        dialog_window.grab_set()
        
        tk.Label(
            dialog_window, text="🎮 Choose AI Difficulty:",
            font=("Segoe UI", 14, "bold"),
            bg="#0f172a", fg="white"
        ).pack(pady=20)

        def select_difficulty(difficulty):
            self.ai_difficulty = difficulty
            dialog_window.destroy()
            self.start_game("PvAI")

        tk.Button(
            dialog_window, text="🍃 Easy",
            font=("Segoe UI", 12, "bold"),
            bg="#10b981", fg="white",
            width=15, pady=8, bd=0,
            command=lambda: select_difficulty("Easy")
        ).pack(pady=5)

        tk.Button(
            dialog_window, text="⚡ Medium",
            font=("Segoe UI", 12, "bold"),
            bg="#3b82f6", fg="white",
            width=15, pady=8, bd=0,
            command=lambda: select_difficulty("Medium")
        ).pack(pady=5)

        tk.Button(
            dialog_window, text="🔥 Hard",
            font=("Segoe UI", 12, "bold"),
            bg="#ef4444", fg="white",
            width=15, pady=8, bd=0,
            command=lambda: select_difficulty("Hard")
        ).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        ConnectFour(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        root.destroy()
