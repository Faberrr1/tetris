import random
import tkinter as tk

WIDTH = 10
HEIGHT = 20
SQUARE_SIZE = 30
DELAY = 500

SHAPES = [[[1, 1, 1, 1]],
          [[1, 1], [1, 1]],
          [[1, 1, 0], [0, 1, 1]],
          [[0, 1, 1], [1, 1, 0]],
          [[1, 1, 1], [0, 1, 0]],
          [[1, 1, 1], [1, 0, 0]],
          [[1, 1, 1], [0, 0, 1]]]

COLORS = ["cyan", "yellow", "green", "red", "blue", "orange", "purple"]


class TetrisGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Tetris")

        self.canvas = tk.Canvas(master, width=WIDTH * SQUARE_SIZE, height=HEIGHT * SQUARE_SIZE)
        self.canvas.pack()

        self.score_label = tk.Label(master, text="Score: 0")
        self.score_label.pack()

        self.level_label = tk.Label(master, text="Level: 1")
        self.level_label.pack()

        self.restart_button = tk.Button(master, text="Spróbuj ponownie", command=self.start_game)
        self.restart_button.pack()

        self.score = 0
        self.level = 1
        self.board = [[0] * WIDTH for _ in range(HEIGHT)]
        self.current_shape = None
        self.current_shape_coords = []
        self.current_shape_ids = []
        self.is_game_over = False

        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)
        self.master.bind("<Down>", self.move_down)
        self.master.bind("<Up>", self.rotate_shape)

        self.start_game()
    def start_game(self):
        self.canvas.delete("game_over")  # Usuwa napis "Game Over"
        self.clear_board()
        self.score = 0
        self.level = 1
        self.is_game_over = False
        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 1")
        self.spawn_shape()
        self.update()


    def clear_board(self):
        self.board = [[0] * WIDTH for _ in range(HEIGHT)]
        self.canvas.delete("block")

    def draw_shape(self, shape, x, y, color):
        block_ids = []
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    block_ids.append(self.draw_block(x + j, y + i, color))
        return block_ids

    def draw_block(self, x, y, color):
        x1 = x * SQUARE_SIZE
        y1 = y * SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE
        y2 = y1 + SQUARE_SIZE
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="block")

    def spawn_shape(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        self.current_shape = shape
        self.current_shape_coords = [WIDTH // 2 - len(shape[0]) // 2, 0]
        self.current_shape_ids = self.draw_shape(shape, self.current_shape_coords[0], self.current_shape_coords[1],
                                                 color)
        self.current_shape_color = color

    def move_left(self, event):
        if self.can_move(self.current_shape, self.current_shape_coords[0] - 1, self.current_shape_coords[1]):
            self.clear_shape()
            self.current_shape_coords[0] -= 1
            self.current_shape_ids = self.draw_shape(self.current_shape, self.current_shape_coords[0],
                                                     self.current_shape_coords[1], self.current_shape_color)

    def move_right(self, event):
        if self.can_move(self.current_shape, self.current_shape_coords[0] + 1, self.current_shape_coords[1]):
            self.clear_shape()
            self.current_shape_coords[0] += 1
            self.current_shape_ids = self.draw_shape(self.current_shape, self.current_shape_coords[0],
                                                     self.current_shape_coords[1], self.current_shape_color)

    def move_down(self, event):
        if self.can_move(self.current_shape, self.current_shape_coords[0], self.current_shape_coords[1] + 1):
            self.clear_shape()
            self.current_shape_coords[1] += 1
            self.current_shape_ids = self.draw_shape(self.current_shape, self.current_shape_coords[0],
                                                     self.current_shape_coords[1], self.current_shape_color)
        else:
            self.freeze_shape()
            lines_cleared = self.check_lines()
            self.spawn_shape()
            if not self.can_move(self.current_shape, self.current_shape_coords[0], self.current_shape_coords[1]):
                self.game_over()
            else:
                self.score += lines_cleared * 100
                self.level = (self.score // 500) + 1
                self.score_label.config(text="Score: {}".format(self.score))
                self.level_label.config(text="Level: {}".format(self.level))

    def rotate_shape(self, event):
        rotated_shape = list(zip(*reversed(self.current_shape)))
        if self.can_move(rotated_shape, self.current_shape_coords[0], self.current_shape_coords[1]):
            self.clear_shape()
            self.current_shape = rotated_shape
            self.current_shape_ids = self.draw_shape(self.current_shape, self.current_shape_coords[0],
                                                     self.current_shape_coords[1], self.current_shape_color)

    def can_move(self, shape, x, y):
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    if (
                            x + j < 0
                            or x + j >= WIDTH
                            or y + i >= HEIGHT
                            or self.board[y + i][x + j]
                    ):
                        return False
        return True

    def clear_shape(self):
        for block_id in self.current_shape_ids:
            self.canvas.delete(block_id)

    def freeze_shape(self):
        for i in range(len(self.current_shape)):
            for j in range(len(self.current_shape[i])):
                if self.current_shape[i][j]:
                    self.board[self.current_shape_coords[1] + i][self.current_shape_coords[0] + j] = 1

    def check_lines(self):
        lines_cleared = 0
        lines_to_clear = []
        for i in range(len(self.board)):
            if all(self.board[i]):
                lines_to_clear.append(i)
        for line in lines_to_clear:
            self.clear_line(line)
            lines_cleared += 1

        for line in sorted(lines_to_clear, reverse=True):
            for block_id in self.canvas.find_withtag("block"):
                _, _, _, block_y = self.canvas.coords(block_id)
                if block_y < line * SQUARE_SIZE:
                    self.canvas.move(block_id, 0, SQUARE_SIZE)
        return lines_cleared

    def clear_line(self, line):
        self.board.pop(line)
        self.board.insert(0, [0] * WIDTH)
        self.canvas.delete("block")

        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j]:
                    x1 = j * SQUARE_SIZE
                    y1 = i * SQUARE_SIZE
                    x2 = x1 + SQUARE_SIZE
                    y2 = y1 + SQUARE_SIZE
                    color = COLORS[self.board[i][j] - 1]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="block")

    def update(self):
        if not self.is_game_over:
            self.move_down(None)
            self.master.after(DELAY - (self.level - 1) * 50, self.update)

    def game_over(self):
        self.is_game_over = True
        self.canvas.create_text(
            WIDTH * SQUARE_SIZE // 2,
            HEIGHT * SQUARE_SIZE // 2,
            text="Game Over",
            font=("Helvetica", 24),
            fill="red",
            tags="game_over",
        )
        self.restart_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    game = TetrisGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
