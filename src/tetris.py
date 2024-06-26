import random
from picographics import PicoGraphics
import msa_input
import screen

print("DEBUG_8")

# = entities ===================================================================

class Board: # pylint: disable=too-many-instance-attributes
    def __init__(self):
        # constants
        self.width = 10
        self.height = screen.HEIGHT
        self.left = (screen.WIDTH - self.width) // 2
        self.initial_fall_speed = 0.6
        self.next_level_speed_factor = 1- 0.2 # increase speed by 20%
        self.t = 0
        self.check_line_interval = 0.5 # rate that lines are cleared
        # init vars
        self.grid = []
        self.move_y_interval = 0
        self.init()

    def init(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.move_y_interval = self.initial_fall_speed

    def is_grid_taken(self, x, y) -> bool:
        if x < 0 or x >= self.width:
            return True
        if y >= self.height:
            return True
        if y < 0:
            return False
        return self.grid[y][x] != 0

    def set_grid_position(self, x, y, pen):
        if (0 <= y < self.height) and (0 <= x < self.width):
            self.grid[y][x] = pen

    def update(self, dt):
        self.t += dt
        if self.t > self.check_line_interval:
            self.t = 0
            for j, row in enumerate(self.grid):
                if all(row):
                    print("line cleared!", j)
                    self.grid.pop(j)
                    self.grid.insert(0, [0 for _ in range(self.width)])
                    self.move_y_interval *= self.next_level_speed_factor

    def draw(self, graphics: PicoGraphics):
        # walls
        graphics.set_pen(screen.PALETTE.white)
        graphics.line(self.left - 1, 0, self.left - 1, self.height)
        graphics.line(self.left + self.width, 0, self.left + self.width, self.height)
        # blocks
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    graphics.set_pen(cell)
                    graphics.pixel(self.left + x, y)

class Block: # pylint: disable=too-many-instance-attributes
    def __init__(self):
        # init
        self.ty = 0
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.shape = []
        self.shape_name = "I"
        self.pen = screen.PALETTE.white
        self.init()

    def init(self):
        name, shape_info = random.choice(list(SHAPES.items()))
        self.shape_name = name
        self.shape = shape_info["shape"]
        self.pen = getattr(screen.PALETTE, shape_info["pen"])
        # start with shape in origin rotation with base line just above board
        self.rotation = 0
        self.x = board.width // 2 - len(self.shape[0]) // 2
        self.y = -len(self.shape)
        self.ty = 0
        for _, row in enumerate(self.shape[::-1]):
            if any(row):
                self.y += 1
                break

    def place_block(self):
        for j, row in enumerate(self.shape):
            for i, cell in enumerate(row):
                if cell:
                    board.set_grid_position(self.x + i, self.y + j, self.pen)
        if self.y < 0:
            print("game over")
            board.init()
        self.init()

    def test_collision(self):
        for j, row in enumerate(self.shape):
            for i, cell in enumerate(row):
                if cell:
                    cx = self.x + i
                    cy = self.y + j
                    if board.is_grid_taken(cx, cy):
                        return True
        return False

    def try_rotate_with_kick(self):
        rule_set = KICK_RULES["I"] if self.shape_name == "I" else KICK_RULES["NOT_I"]
        rules = rule_set[self.rotation % 4]
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]
        xo = self.x
        yo = self.y
        for rule in rules:
            dx, dy = rule
            self.x = xo + dx # dx is right-wards
            self.y = yo - dy # dy is up-wards
            if not self.test_collision():
                self.rotation += 1
                return True
        self.shape = list(reversed(list(zip(*self.shape))))
        self.x = xo
        self.y = yo
        return False

    def update(self, dt):
        # rotate
        if msa_input.get_jump(dt):
            if self.try_rotate_with_kick():
                pass
            else:
                print("rotate blocked")

        # x movement
        input_x = msa_input.get_tilt_as_ticking_button(dt)
        if input_x < 0:
            self.x -= 1
        elif input_x > 0:
            self.x += 1

        if input_x != 0:
            if self.test_collision():
                if input_x < 0:
                    self.x += 1
                elif input_x > 0:
                    self.x -= 1

        # fall
        self.ty += dt
        if self.ty > board.move_y_interval:
            self.ty = 0
            self.y += 1
            if self.test_collision():
                self.y -= 1
                self.place_block()

    def draw(self, graphics: PicoGraphics):
        for j, row in enumerate(self.shape):
            for i, cell in enumerate(row):
                if cell:
                    dx = self.x + i + board.left
                    dy = self.y + j
                    graphics.set_pen(self.pen)
                    graphics.pixel(dx, dy)

# = resources ==================================================================

KICK_RULES = {
    "NOT_I": [
        [[0,0], [-1,0], [-1, 1], [0,-2], [-1,-2]], # O -> R
        [[0,0], [ 1,0], [ 1,-1], [0, 2], [ 1, 2]], # R -> 2
        [[0,0], [ 1,0], [ 1, 1], [0,-2], [ 1,-2]], # 2 -> L
        [[0,0], [-1,0], [-1,-1], [0, 2], [-1, 2]], # L -> O
    ],
    "I": [
        [[0,0], [-2,0], [ 1,0], [-2,-1], [ 1, 2]], # O -> R
        [[0,0], [-1,0], [ 2,0], [-1, 2], [ 2,-1]], # R -> 2
        [[0,0], [ 2,0], [-1,0], [ 2, 1], [-1,-2]], # 2 -> L
        [[0,0], [ 1,0], [-2,0], [ 1,-2], [-2, 1]], # L -> O
    ]
}

SHAPES = {
    "I": {
        "shape": [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        "pen": "cyan"
    },
    "J": {
        "shape": [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "blue"
    },
    "L": {
        "shape": [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "orange"
    },
    "O": {
        "shape": [
            [1, 1],
            [1, 1],
        ],
        "pen": "yellow"
    },
    "S": {
        "shape": [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0],
        ],
        "pen": "green"
    },
    "T": {
        "shape": [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0],
        ],
        "pen": "purple"
    },
    "Z": {
        "shape": [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0],
        ],
        "pen": "red"
    }
}

# = game loop ===================================================================

# init
board: Board
tetromino: Block

# loop

def init():
    global board, tetromino # pylint: disable=global-statement
    board = Board()
    tetromino = Block()

def update(dt):
    board.update(dt)
    tetromino.update(dt)

def draw(graphics: PicoGraphics):
    board.draw(graphics)
    tetromino.draw(graphics)
