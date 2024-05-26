import math
import random
from stellar import StellarUnicorn
from picographics import PicoGraphics
from breakout_msa311 import BreakoutMSA311

# = setup ======================================================================

print("debug string 456")

PALETTE = {}
SCREEN_WIDTH = StellarUnicorn.WIDTH
SCREEN_HEIGHT = StellarUnicorn.HEIGHT

# = entities ===================================================================

class Board:
    def __init__(self):
        self.width = 10
        self.height = SCREEN_HEIGHT
        self.x0 = (SCREEN_WIDTH - self.width) // 2
        self.grid = [[0 for x in range(self.width)] for y in range(self.height)]

    def draw(self, graphics: PicoGraphics):
        # walls
        graphics.set_pen(PALETTE["WHITE"])
        graphics.line(self.x0 - 1, 0, self.x0 - 1, self.height)
        graphics.line(self.x0 + self.width, 0, self.x0 + self.width, self.height)
        # blocks
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    graphics.set_pen(cell)
                    graphics.pixel(self.x0 + x, y)

class Tetromino:
    def __init__(self):
        # constants
        self.v_max = SCREEN_WIDTH * 2.5
        self.input_min = 0.075
        self.input_max = 0.6
        self.input_f = self.v_max / (self.input_max - self.input_min)
        # globals
        self.vx = 0.2 # five moves per second
        self.vy = 0.25
        self.tx = 0
        self.ty = 0
        # shape
        self.shape = []
        self.pen = None
        self.x = 0
        self.y = 0
        self.init()

    def init(self):
        _, shape_info = random.choice(list(SHAPES.items()))
        self.shape = shape_info["shape"]
        self.pen = PALETTE[shape_info["pen"]]
        # start with shape base at top of board
        self.x = board.width // 2 - len(self.shape[0]) // 2
        self.y = -len(self.shape)
        for _, row in enumerate(self.shape[::-1]):
            if any(row):
                self.y += 1
                break

    def freeze(self):
        for j, row in enumerate(self.shape):
            for i, cell in enumerate(row):
                if cell:
                    board.grid[self.y + j][self.x + i] = self.pen
        self.init()

    def update(self, msa: BreakoutMSA311, dt):
        # x-movement
        self.tx += dt
        target_v = 0
        if self.tx > self.vx:
            self.tx = 0
            input_x = -1 * msa.get_x_axis() # x axis is inverted
            clamp_x = max(min(abs(input_x), self.input_max), self.input_min) - self.input_min
            target_v = math.copysign(
                clamp_x, # clamp
                input_x # re-sign
            )
            if target_v < 0:
                self.x -= 1
            elif target_v > 0:
                self.x += 1

        # x collision
        if target_v != 0:
            for j, row in enumerate(self.shape):
                for i, cell in enumerate(row):
                    if cell:
                        if self.x + i < 0:
                            self.x += 1
                        elif self.x + i >= board.width:
                            self.x -= 1
                        elif self.y + j < 0:
                            pass
                        elif self.y + j >= board.height:
                            pass
                        elif board.grid[self.y + j][self.x + i]:
                            if target_v < 0:
                                self.x += 1
                            elif target_v > 0:
                                self.x -= 1

        # y-movement
        self.ty += dt
        target_v = 0
        if self.ty > self.vy:
            self.ty = 0
            self.y += 1
            target_v = 1

        # y collision
        if target_v != 0:
            for j, row in enumerate(self.shape):
                for i, cell in enumerate(row):
                    if cell:
                        if self.y + j >= board.height:
                            self.y -= 1
                            self.freeze()
                            return
                        if self.y + j >= 0 and board.grid[self.y + j][self.x + i]:
                            self.y -= 1
                            self.freeze()
                            return

    def draw(self, graphics: PicoGraphics):
        for j, row in enumerate(self.shape):
            for i, cell in enumerate(row):
                if cell:
                    dx = self.x + i + board.x0
                    dy = self.y + j
                    graphics.set_pen(self.pen)
                    graphics.pixel(dx, dy)

# = resources ==================================================================

SHAPES = {
    "I": {
        "shape": [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        "pen": "CYAN"
    },
    "J": {
        "shape": [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "BLUE"
    },
    "L": {
        "shape": [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "ORANGE"
    },
    "O": {
        "shape": [
            [1, 1],
            [1, 1],
        ],
        "pen": "YELLOW"
    },
    "S": {
        "shape": [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0],
        ],
        "pen": "GREEN"
    },
    "T": {
        "shape": [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "PURPLE"
    },
    "Z": {
        "shape": [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0],
        ],
        "pen": "RED"
    }
}

# = game loop ===================================================================

# init
board: Board
tetromino: Tetromino

# loop

def init():
    global board, tetromino
    board = Board()
    tetromino = Tetromino()

def update(msa: BreakoutMSA311, dt):
    tetromino.update(msa, dt)

def draw(graphics: PicoGraphics):
    board.draw(graphics)
    tetromino.draw(graphics)