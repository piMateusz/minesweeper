import pygame
import os
import random
from typing import List

pygame.init()

screen_width = 500
screen_height = 650
bomb_amount = 10
flag_amount = 10
clock_time = 0

menu_height = 150
tile_size = 50
score_file = 'score.txt'

rows = int(screen_width/tile_size)   # 20 rows
cols = int((screen_height-menu_height)/tile_size)     # 20 cols

win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Minesweeper')

# board marks:
# 0 - empty cell
# 1 - one bomb around, 2 - two bombs around, etc.
# 'b' - bomb here
# 'blocked' - tile visible after 1st touch, where we can't randomly create bomb (to avoid losing in 1st touch)


class Minesweeper:
    def __init__(self, board):
        self.first_touch_number = 2     # blocked tiles after 1st touch
        self.board = board
        self.visible = set()
        self.is_bomb = False
        self.bombs = {}             # (x, y) : <bomb object>
        self.tiles = {}             # (x, y) : <tile object>
        self.flags = {}             # (x, y) : <flag object>
        self.number_tiles = {}      # (x, y): <number_tile object>
        self.flag_counter = 0
        self.mode = 'Easy'        # setting difficulty to easy

    def randomize_board(self):
        # fill board with random bombs
        for bomb_count in range(bomb_amount):
            random_x = random.randint(0, rows - 1)
            random_y = random.randint(0, cols - 1)
            while self.board[random_x][random_y] == 'b' or self.board[random_x][random_y] == 'blocked':
                random_x = random.randint(0, rows - 1)
                random_y = random.randint(0, cols - 1)
            self.board[random_x][random_y] = 'b'
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] == 'blocked':
                    self.board[row][col] = 0

        # fill board with appropriate numbers (1, 2, 3, etc.)
        for row in range(rows):
            for col in range(cols):
                counter = 0
                if self.board[row][col] != 'b':
                    for x in range(row - 1, row + 2):
                        if 0 <= x < rows:
                            for y in range(col - 1, col + 2):
                                if 0 <= y < cols:
                                    if x == row and y == col:
                                        continue
                                    if self.board[x][y] == 'b':
                                        counter += 1
                    self.board[row][col] = counter

    def count_and_draw_flags(self, win):
        self.flag_counter = flag_amount - len(self.flags)
        font = pygame.font.SysFont('comicsans', 50)
        text = font.render(str(self.flag_counter), 1, (255, 0, 0))
        win.blit(text, (screen_width/2 + 25, screen_height - menu_height / 2 - 15, tile_size, tile_size))

    # converts board to graphical interface (adds tiles, bombs, number_tiles and flags objects to dictionaries
    # if they are not in yet)
    def convert(self):
        for row in range(rows):
            for col in range(cols):
                if (row, col) in self.visible:
                    if self.board[row][col] == 'b' and (row, col) not in self.bombs:
                        bomb = Tile(row*tile_size + 1, col*tile_size + 1, tile_size - 2, tile_size - 2,
                                    pygame.image.load(os.path.join('images', self.mode + 'Mine.png')))
                        self.bombs[(row, col)] = bomb
                    if self.board[row][col] == 0 and (row, col) not in self.tiles:
                        tile = Tile(row*tile_size + 1, col*tile_size + 1, tile_size - 2, tile_size - 2,
                                    pygame.image.load(os.path.join('images', self.mode + 'Tile.png')).convert())
                        self.tiles[(row, col)] = tile
                    elif self.board[row][col] != 0 and self.board[row][col] != 'b' \
                            and (row, col) not in self.number_tiles:
                        number = str(self.board[row][col])
                        number_tile = Number(row*tile_size + 1, col*tile_size + 1, tile_size - 2, tile_size - 2, number,
                                             pygame.image.load(os.path.join('images', self.mode + 'Tile.png')).convert())
                        self.number_tiles[(row, col)] = number_tile
                elif (row, col) in self.flags and not self.flags[(row, col)]:
                    flag = Tile(row*tile_size + 1, col*tile_size + 1, tile_size - 2, tile_size - 2,
                                pygame.image.load(os.path.join('images', self.mode + 'Flag.png')).convert())
                    self.flags[(row, col)] = flag

    # drawing bombs, tiles and flags on screen
    def draw(self, win):
        for bomb in self.bombs:
            self.bombs[bomb].draw(win)
        for tile in self.tiles:
            self.tiles[tile].draw(win)
        for number_tile in self.number_tiles:
            self.number_tiles[number_tile].draw_number(win)
        for flag in self.flags:
            self.flags[flag].draw(win)

    def reset_game(self):
        global clock_time
        clock_time = 0
        self.board = create_board()
        self.is_bomb = False
        self.flags = {}
        self.bombs = {}
        self.tiles = {}
        self.number_tiles = {}
        self.visible = set()

    # ending screen - displays either when you lost or won
    def ending_screen(self, text):
        play = True
        global run

        trophy_img = pygame.image.load(os.path.join('images', 'Trophy.png'))
        clock_img = pygame.image.load(os.path.join('images', 'clock.png'))

        win.fill((0, 0, 0))

        pygame.draw.rect(win, (255, 255, 255), (screen_width/2 - 100, screen_height/2 - 150, 200, 300))
        pygame.draw.rect(win, (255, 0, 0), (screen_width/2 - 100, screen_height/2 - 150, 200, 300), 2)
        font = pygame.font.SysFont('comicsans', 20)

        title = font.render(text, 1, (0, 0, 0))
        win.blit(title, (screen_width/2 - title.get_width()/2, 200))
        score = str(0)
        if text == 'You won!':
            score = str(clock_time)
        score_text = font.render(score, 1, (0, 0, 0))
        win.blit(score_text, (screen_width/2 - 55, 250))
        win.blit(clock_img, (screen_width/2 - 75, 275))

        high_score = get_high_score(score_file)
        high_score_text = font.render(str(high_score), 1, (0, 0, 0))
        win.blit(high_score_text, (screen_width/2 + 45, 250))
        win.blit(trophy_img, (screen_width/2 + 25, 275))

        play_again_button = PygameButton(screen_width/2 - 50, screen_height/2 + 15, 100, 50, 'Play Again')
        exit_button = PygameButton(screen_width/2 - 50, screen_height/2 + 85, 100, 50, 'Exit')

        while play:
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    play = False
                    run = False
                    reset_high_score(score_file)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.on_click(pos):
                        pygame.time.delay(1000)
                        self.reset_game()
                        play = False
                    if exit_button.on_click(pos):
                        play = False
                        run = False
                        reset_high_score(score_file)

            play_again_button.draw(win)
            exit_button.draw(win)
            pygame.display.update()

    # Depth first search algorithm
    def dfs(self, x, y):
        neighbour_stack = [(x, y)]
        while neighbour_stack:
            new_stack = []
            x, y = neighbour_stack.pop(0)
            if (x, y) not in self.visible:
                self.visible.add((x, y))
            for i in range(x - 1, x + 2):
                if 0 <= i < rows:
                    for j in range(y - 1, y + 2):
                        if 0 <= j < cols:
                            if i == x and j == y:
                                continue
                            if (i, j) not in self.flags:
                                if self.board[i][j] == 0 and (i, j) not in self.visible:
                                    new_stack.append((i, j))
                                elif self.board[i][j] != 'b':
                                    self.visible.add((i, j))
            neighbour_stack = new_stack + neighbour_stack

    # refreshes the board
    def refresh(self):
        # action of clicking mouse here and reaction on this
        keys = pygame.mouse.get_pressed()
        if keys[0]:         # left mouse button clicked
            x, y = pygame.mouse.get_pos()
            if easy_button.on_click((x, y)) and self.mode != 'Easy':        # changing difficulty to easy
                self.mode = 'Easy'
                easy_button.change_mode()
            if medium_button.on_click((x, y)) and self.mode != 'Medium':    # changing difficulty to medium
                self.mode = 'Medium'
                medium_button.change_mode()
            if hard_button.on_click((x, y)) and self.mode != 'Hard':        # changing difficulty to hard
                self.mode = 'Hard'
                hard_button.change_mode()
            if y <= screen_height - menu_height:            # if we click on the main game board
                x = x//tile_size
                y = y//tile_size
                if not self.visible:                        # handling users 1st touch
                    if self.mode == 'easy':
                        self.first_touch_number = 2
                    if self.mode == 'medium':
                        self.first_touch_number = 3
                    if self.mode == 'hard':
                        self.first_touch_number = 4
                    for j in range(-1, self.first_touch_number):
                        if 0 <= x + j < rows:
                            for k in range(-1, self.first_touch_number):
                                if 0 <= y + k < cols:
                                    self.board[x + j][y + k] = 'blocked'
                    self.randomize_board()
                    self.dfs(x, y)
                else:
                    if (x, y) not in self.flags:
                        if self.board[x][y] != 0:
                            self.visible.add((x, y))
                            if self.board[x][y] == 'b':
                                self.is_bomb = True
                                for row in range(rows):
                                    for col in range(cols):
                                        if self.board[row][col] == 'b':
                                            self.visible.add((row, col))
                        else:
                            # clearing flags and flag count if only flags are visible
                            if len(self.visible) == len(self.number_tiles) and len(self.flags.keys()) > 0:
                                self.flags = {}
                                self.flag_counter = flag_amount
                            self.dfs(x, y)

        if keys[2]:                                         # right mouse button clicked
            x, y = pygame.mouse.get_pos()
            if y <= screen_height - menu_height:            # if we click on the main game board
                x = x // tile_size
                y = y // tile_size
                pygame.time.delay(150)
                if (x, y) not in self.visible:
                    if (x, y) not in self.flags:
                        self.flags[(x, y)] = False          # adding flags
                    else:
                        del self.flags[(x, y)]              # deleting flags


class Tile:
    def __init__(self, x, y, width, height, img):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))


class Number(Tile):
    def __init__(self, x, y, width, height, number, img):
        super().__init__(x, y, width, height, img)
        self.number = number

    def draw_number(self, win):
        font = pygame.font.SysFont('comicsans', 30)
        text = font.render(self.number, 1, (0, 0, 0))
        self.draw(win)
        win.blit(text, (int(self.x + self.width/2 - text.get_width() / 2),
                        int(self.y + self.height/2 - text.get_height() / 2)))


class PygameButton:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        font = pygame.font.SysFont('comicsans', 20)
        text = font.render(self.text, 1, (255, 0, 0))
        win.blit(text, (int(self.x + self.width/2 - text.get_width()/2),
                        int(self.y + self.height/2 - text.get_height()/2)))

    def on_click(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False


class DifficultyButton(PygameButton):
    def __init__(self, x, y, width, height, text, bomb_amount_, flag_amount_, screen_width_, screen_height_, tile_size_):
        super().__init__(x, y, width, height, text)
        self.bomb_amount_ = bomb_amount_
        self.flag_amount_ = flag_amount_
        self.screen_width_ = screen_width_
        self.screen_height_ = screen_height_
        self.tile_size_ = tile_size_

    def change_mode(self):
        global mode_changed, bomb_amount, screen_width, screen_height, flag_amount, tile_size, rows, cols, run
        bomb_amount = self.bomb_amount_
        screen_width = self.screen_width_
        screen_height = self.screen_height_
        flag_amount = self.flag_amount_
        tile_size = self.tile_size_
        rows = int(screen_width / tile_size)
        cols = int((screen_height - menu_height) / tile_size)
        mode_changed = True
        run = False
        minesweeper.reset_game()
        reset_high_score(score_file)


def create_board() -> List[List[int]]:
    # create board (2 - dim array filled with 0)
    board = [[0 for row in range(rows)] for col in range(cols)]
    return board


def create_grid(win):
    for row in range(rows+1):
        pygame.draw.line(win, (0, 0, 0), (0, row*tile_size), (screen_width, row*tile_size))
        pygame.draw.line(win, (0, 0, 0), (row * tile_size, 0), (row * tile_size, screen_height-menu_height))


def draw_time(win):
    font = pygame.font.SysFont('comicsans', 50)
    text = font.render(str(clock_time), 1, (255, 0, 0))
    win.blit(text,
             (screen_width / 2 + 175, screen_height - menu_height / 2 - 15, 50, 50))


# updating score in score_file
def score_update(file_name):
    best_score = get_high_score(file_name)
    if best_score != 0:
        if best_score > clock_time:
            with open(file_name, 'w') as f:
                f.write(str(clock_time))
    else:
        with open(file_name, 'w') as f:
            f.write(str(clock_time))


def get_high_score(file_name):
    best_score = 0
    with open(file_name, 'r') as file:
        for line in file:
            best_score = int(line)
    return best_score


def reset_high_score(file_name):
    with open(file_name, 'w') as file:
        file.write(str(0))


# redraws game window, function used in mainloop in every iteration
def redraw_game_window(win):
    win.fill((255, 255, 255))

    # handling main game board
    create_grid(win)
    minesweeper.refresh()
    minesweeper.convert()

    # drawing
    minesweeper.draw(win)
    minesweeper.count_and_draw_flags(win)
    easy_button.draw(win)
    medium_button.draw(win)
    hard_button.draw(win)
    flag_main_img.draw(win)
    clock_main_img.draw(win)
    draw_time(win)
    pygame.display.update()

    # checking if we hit bomb
    if minesweeper.is_bomb:
        pygame.time.delay(1000)
        # displaying ending screen
        minesweeper.ending_screen('You lost!')

    # checking if we win
    if len(minesweeper.visible) == rows * cols - bomb_amount:
        score_update(score_file)
        # displaying ending screen
        minesweeper.ending_screen('You won!')


board = create_board()
minesweeper = Minesweeper(board)
easy_button = DifficultyButton(50, 520, 100, 30, 'Easy', 10, 10, 500, 650, 50)       # change to difficulty button later
medium_button = DifficultyButton(50, 560, 100, 30, 'Medium', 35, 35, 510, 660, 34)   # change to difficulty button later
hard_button = DifficultyButton(50, 600, 100, 30, 'Hard', 80, 80, 520, 670, 26)       # change to difficulty button later
flag_main_img = Tile(screen_width/2 - tile_size, screen_height - menu_height / 2 - tile_size/2, tile_size, tile_size,
                     pygame.image.load(os.path.join('images', 'EasyFlag.png')).convert())
clock_main_img = Tile(screen_width/2 + 2*tile_size, screen_height - menu_height / 2 - tile_size/2, tile_size, tile_size,
                      pygame.image.load(os.path.join('images', 'clock.png')))

pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # setting timer for 1 sec.

run = True
mode_changed = False


def main():
    global clock_time, run, win, mode_changed, easy_button, medium_button, hard_button, flag_main_img, clock_main_img

    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Minesweeper')

    easy_button = DifficultyButton(50, screen_height - 130, 100, 30, 'Easy', 10, 10, 500, 650, 50)
    medium_button = DifficultyButton(50, screen_height - 90, 100, 30, 'Medium', 35, 35, 510, 660, 34)
    hard_button = DifficultyButton(50, screen_height - 50, 100, 30, 'Hard', 80, 80, 520, 670, 26)
    flag_main_img = Tile(screen_width / 2 - 50, screen_height - menu_height / 2 - 50 / 2, 50,
                         50,
                         pygame.image.load(os.path.join('images', 'EasyFlag.png')).convert())
    clock_main_img = Tile(screen_width / 2 + 100, screen_height - menu_height / 2 - 25, 50,
                          50,
                          pygame.image.load(os.path.join('images', 'clock.png')))

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.USEREVENT + 1:
                if minesweeper.visible or minesweeper.flags:
                    clock_time += 1

        redraw_game_window(win)

    if not mode_changed:
        pygame.quit()
    else:
        mode_changed = False
        run = True
        main()


if __name__ == "__main__":
    main()

