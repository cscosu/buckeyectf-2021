from enum import IntFlag
from collections import namedtuple
import random
import gmpy2
import Crypto.Util.number as cun
from copy import deepcopy


class Dir(IntFlag):
    U = 1
    D = 2
    L = 4
    R = 8


class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


def vec2_to_dir(v: Vec2) -> Dir:
    return {
        Vec2(0, -1): Dir.U,
        Vec2(0, 1): Dir.D,
        Vec2(-1, 0): Dir.L,
        Vec2(1, 0): Dir.R,
    }[v]


def dir_to_vec2(d: Dir) -> Vec2:
    return {
        Dir.U: Vec2(0, -1),
        Dir.D: Vec2(0, 1),
        Dir.L: Vec2(-1, 0),
        Dir.R: Vec2(1, 0),
    }[d]


def opposite_dir(d: Dir) -> Dir:
    return {
        Dir.U: Dir.D,
        Dir.D: Dir.U,
        Dir.L: Dir.R,
        Dir.R: Dir.L,
    }[d]


# `cur` and `pos` have type Vec2
Node = namedtuple("Node", ["cur", "prev"])

ROWS = 10
COLS = 10


def in_grid(grid, v: Vec2):
    rows = len(grid)
    cols = len(grid[0])
    return 0 <= v.x < cols and 0 <= v.y < rows


def node_child(n: Node, d: Dir):
    return Node(n.cur + dir_to_vec2(d), n.cur)


def generate_dir_grid():
    grid = [[0] * COLS for _ in range(ROWS)]
    visited = set()
    queue = [Node(Vec2(0, 0), Vec2(0, -1))]

    while len(queue) > 0:
        n = queue.pop()
        if n.cur in visited:
            continue
        visited.add(n.cur)

        dir_to_prev = vec2_to_dir(n.prev - n.cur)
        grid[n.cur.y][n.cur.x] |= dir_to_prev
        if in_grid(grid, n.prev):
            grid[n.prev.y][n.prev.x] |= opposite_dir(dir_to_prev)

        neighbors = [
            node_child(n, Dir.U),
            node_child(n, Dir.D),
            node_child(n, Dir.L),
            node_child(n, Dir.R),
        ]

        neighbors = list(
            filter(lambda n: in_grid(grid, n.cur) and n.cur not in visited, neighbors)
        )
        random.shuffle(neighbors)

        for neighbor in neighbors:
            queue.append(neighbor)

    grid[ROWS - 1][COLS - 1] |= Dir.D
    return grid


def generate_bool_grid(dir_grid):
    grid = [[1] * (2 * COLS + 1) for _ in range(2 * ROWS + 1)]
    for row in range(ROWS):
        for col in range(COLS):
            # Center
            c = Vec2(2 * col + 1, 2 * row + 1)
            grid[c.y + 0][c.x + 0] = 0

            d = dir_grid[row][col]

            if Dir.U in d:
                grid[c.y - 1][c.x + 0] = 0
            if Dir.D in d:
                grid[c.y + 1][c.x + 0] = 0
            if Dir.L in d:
                grid[c.y + 0][c.x - 1] = 0
            if Dir.R in d:
                grid[c.y + 0][c.x + 1] = 0

    return grid


def bfs(bool_grid):
    rows = len(bool_grid)
    cols = len(bool_grid[0])

    pos = Vec2(1, 0)
    end = Vec2(cols - 2, rows - 1)

    queue = [[pos]]

    while len(queue) > 0:
        path = queue.pop()
        if path[-1] == end:
            return path

        neighbors = [
            path[-1] + Vec2(0, -1),
            path[-1] + Vec2(0, 1),
            path[-1] + Vec2(-1, 0),
            path[-1] + Vec2(1, 0),
        ]

        def f(p):
            return in_grid(bool_grid, p) and p not in path and bool_grid[p.y][p.x] == 0  # type: ignore

        neighbors = list(filter(f, neighbors))

        neighbors = [path + [p] for p in neighbors]
        queue = neighbors + queue


def count_branches(bool_grid, path):
    ans = 0
    for p in path:
        neighbors = [
            p + Vec2(0, -1),
            p + Vec2(0, 1),
            p + Vec2(-1, 0),
            p + Vec2(1, 0),
        ]

        def f(p):
            return in_grid(bool_grid, p) and p not in path and bool_grid[p.y][p.x] == 0

        neighbors = list(filter(f, neighbors))

        ans += len(neighbors)

    return ans


if __name__ == "__main__":
    max_branches = 0
    while True:
        dir_grid = generate_dir_grid()
        bool_grid = generate_bool_grid(dir_grid)

        path = bfs(bool_grid)
        n_branches = count_branches(bool_grid, path)
        max_branches = max(n_branches, max_branches)
        solved_grid = deepcopy(bool_grid)

        for p in path:
            solved_grid[p.y][p.x] = 2

        s = {0: " ", 1: "#", 2: "-"}

        for row in solved_grid:
            print(" ".join(s[x] for x in row))

        print(f"n_branches = {n_branches}")
        print(f"max_branches = {max_branches}")

        if n_branches >= 13:
            print("Done")
            break

    blobs = []
    for row in bool_grid:
        s = ", ".join(str(x) for x in row)
        blob = f"{{{s}}}"
        blobs.append(blob)

    blob = ", ".join(blobs)
    dec = f"private static final int grid[][] = {{{blob}}};"
    print(dec)
