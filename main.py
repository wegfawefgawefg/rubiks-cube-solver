from collections import deque
import itertools
from pprint import pprint
import random
import time
from colorama import Fore, Style
from enum import Enum, auto


# facecode enum
class FaceCode(Enum):
    U = auto()
    D = auto()
    L = auto()
    R = auto()
    F = auto()
    B = auto()


class Face:
    def __init__(self, color) -> None:
        self.cells = [[color for _ in range(3)] for _ in range(3)]

    def set_cells(self, cells):
        self.cells = cells

    def make_clock_face(self, offset):
        idxs = ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0))
        for i, (y, x) in enumerate(idxs):
            self.cells[y][x] = (i + offset) % 8

    def make_checker_face(self, color_a, color_b):
        for y in range(3):
            for x in range(3):
                if (x + y) % 2 == 0:
                    self.cells[y][x] = color_a
                else:
                    self.cells[y][x] = color_b

    def rotate(self):
        rotated_face = [[0 for _ in range(3)] for _ in range(3)]
        for y in range(3):
            for x in range(3):
                rotated_face[x][2 - y] = self.cells[y][x]
        self.cells = rotated_face

    def get_top_edge(self):
        return [self.cells[0][i] for i in range(3)]

    def get_bottom_edge(self):
        return [self.cells[2][i] for i in range(3)]

    def get_left_edge(self):
        return [row[0] for row in self.cells]

    def get_right_edge(self):
        return [row[2] for row in self.cells]

    def set_top_edge(self, edge):
        self.cells[0] = edge

    def set_bottom_edge(self, edge):
        self.cells[2] = edge

    def set_left_edge(self, edge):
        for i, cell in enumerate(edge):
            row = self.cells[i]
            row[0] = cell

    def set_right_edge(self, edge):
        for i, cell in enumerate(edge):
            row = self.cells[i]
            row[2] = cell

    def __eq__(self, other_face):
        for y in range(3):
            for x in range(3):
                if self.cells[y][x] != other_face.cells[y][x]:
                    return False
        return True


class Cube:
    FACE_CODE_TO_INDEX = {"U": 0, "D": 1, "L": 2, "R": 3, "F": 4, "B": 5}
    SOLVED = [Face(color) for color in range(6)]
    FACES = ["U", "D", "L", "R", "F", "B"]
    FACE_ADJACENCIES = {
        "F": ["U", "R", "D", "L"],
        "B": ["U", "L", "D", "R"],
        "U": ["B", "R", "F", "L"],
        "D": ["F", "R", "B", "L"],
        "L": ["U", "F", "D", "B"],
        "R": ["U", "B", "D", "F"],
    }
    INT_TO_TERM_COLOR = {
        0: Fore.YELLOW,
        1: Fore.WHITE,
        2: Fore.GREEN,
        3: Fore.BLUE,
        4: Fore.RED,
        5: Fore.MAGENTA,
        6: Fore.BLACK,
        7: Fore.CYAN,
    }

    def __init__(self):
        self.faces = [Face(color) for color in range(6)]

    def scramble(self, moves=100):
        for _ in range(moves):
            self.rotate_face(random.choice(Cube.FACES))
        return self

    def clock_faces(self):
        [face.make_clock_face(i) for i, face in enumerate(self.faces)]
        return self

    def checker(self):
        [
            face.make_checker_face(face.cells[0][0], random.choice(list(range(6))))
            for face in self.faces
        ]
        return self

    def is_win(self):
        for win_face, face in zip(self.SOLVED, self.faces):
            if win_face != face:
                return False
        return True

    def rate(self):
        correctness = 0
        for solved_face, face in zip(self.SOLVED, self.faces):
            for solved_row, row in zip(solved_face.cells, face.cells):
                for solved_cell, cell in zip(solved_row, row):
                    if solved_cell == cell:
                        correctness += 1
        return correctness

    def get_face(self, face_code):
        return self.faces[self.FACE_CODE_TO_INDEX[face_code]]

    def print(self):
        face_codes_to_print = [
            (None, "U", None, None),
            ("L", "F", "R", "B"),
            (None, "D", None, None),
        ]

        buffer = [[None for _ in range(12)] for _ in range(9)]
        for grid_y, row in enumerate(face_codes_to_print):
            for grid_x, face_code in enumerate(row):
                grid_offset_y = grid_y * 3
                grid_offset_x = grid_x * 3
                if face_code == None:
                    for y in range(0, 3):
                        for x in range(0, 3):
                            buffer[grid_offset_y + y][grid_offset_x + x] = 9
                else:
                    face = self.get_face(face_code)
                    for face_y, face_row in enumerate(face.cells):
                        for face_x, color in enumerate(face_row):
                            buffer[grid_offset_y + face_y][
                                grid_offset_x + face_x
                            ] = color
        # pprint(buffer)
        for row in buffer:
            for color in row:
                if color == 9:
                    print(Fore.BLACK + "□" + Style.RESET_ALL, end=" ")
                else:
                    print(
                        Cube.INT_TO_TERM_COLOR[color] + "■" + Style.RESET_ALL, end=" "
                    )
            print()

    def rotate_face(self, face_code):
        face = self.faces[Cube.FACE_CODE_TO_INDEX[face_code]]
        rotated_face = [[0 for _ in range(3)] for _ in range(3)]
        for y in range(3):
            for x in range(3):
                rotated_face[x][2 - y] = face.cells[y][x]
        face.cells = rotated_face
        self._rotate_adjacent_faces(face_code)

    def _rotate_adjacent_faces(self, face_code):
        # Rotate adjacent rows/columns of the nearby faces
        # for simplicity, hardcode these
        # this is probably faster, but impure, and wont generalize to other puzzles
        # realistically this needs to be shrunk to a 1d array of bytes with fixed ops
        if face_code == "F":
            # the right side of l becomes bottom of u
            # the bottom of u becomes the left side of r
            # the left side of r becomes the top of d
            # the top of d becomes the right side of l

            # extract
            l, u, r, d = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "LURD"
            ]
            l_r, u_b, r_l, d_t = (
                l.get_right_edge(),
                u.get_bottom_edge(),
                r.get_left_edge(),
                d.get_top_edge(),
            )
            # align
            l_r.reverse()
            r_l.reverse()
            # assign
            l.set_right_edge(d_t)
            u.set_bottom_edge(l_r)
            r.set_left_edge(u_b)
            d.set_top_edge(r_l)
        elif face_code == "U":
            # f_t becomes r_t
            # r_t becomes b_t
            # b_t becomes l_t
            # l_t becomes f_t

            # extract
            f, r, b, l = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "FRBL"
            ]
            f_t, r_t, b_t, l_t = (
                f.get_top_edge(),
                r.get_top_edge(),
                b.get_top_edge(),
                l.get_top_edge(),
            )
            # assign
            f.set_top_edge(r_t)
            r.set_top_edge(b_t)
            b.set_top_edge(l_t)
            l.set_top_edge(f_t)
        elif face_code == "D":
            # f_b becomes l_b
            # l_b becomes b_b
            # b_b becomes r_b
            # r_b becomes f_b

            # extract
            f, r, b, l = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "FRBL"
            ]
            f_b, r_b, b_b, l_b = (
                f.get_bottom_edge(),
                r.get_bottom_edge(),
                b.get_bottom_edge(),
                l.get_bottom_edge(),
            )
            # assign
            f.set_bottom_edge(l_b)
            r.set_bottom_edge(f_b)
            b.set_bottom_edge(r_b)
            l.set_bottom_edge(b_b)
        elif face_code == "L":
            # f_l becomes u_l
            # u_l becomes b_r
            # b_r becomes d_l
            # d_l becomes f_l

            # extract
            f, u, b, d = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "FUBD"
            ]
            f_l, u_l, b_r, d_l = (
                f.get_left_edge(),
                u.get_left_edge(),
                b.get_right_edge(),
                d.get_left_edge(),
            )
            # assign
            f.set_left_edge(u_l)
            u.set_left_edge(b_r)
            b.set_right_edge(d_l)
            d.set_left_edge(f_l)
        elif face_code == "R":
            # f_r becomes d_r
            # d_r becomes b_l
            # b_l becomes u_r
            # u_r becomes f_r

            # extract
            f, u, b, d = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "FUBD"
            ]
            f_r, u_r, b_l, d_r = (
                f.get_right_edge(),
                u.get_right_edge(),
                b.get_left_edge(),
                d.get_right_edge(),
            )
            # align
            u_r.reverse()
            b_l.reverse()
            # assign
            f.set_right_edge(d_r)
            u.set_right_edge(f_r)
            b.set_left_edge(u_r)
            d.set_right_edge(b_l)
        elif face_code == "B":
            # u_t becomes r_r
            # r_r becomes d_b
            # d_b becomes l_l
            # l_l becomes u_t

            # extract
            u, r, d, l = [
                self.faces[Cube.FACE_CODE_TO_INDEX[face_code]] for face_code in "URDL"
            ]
            u_t, r_r, d_b, l_l = (
                u.get_top_edge(),
                r.get_right_edge(),
                d.get_bottom_edge(),
                l.get_left_edge(),
            )
            # align
            u_t.reverse()
            l_l.reverse()
            # assign
            u.set_top_edge(r_r)
            r.set_right_edge(d_b)
            d.set_bottom_edge(l_l)
            l.set_left_edge(u_t)

    def animate(self):
        while True:
            for move in moves:
                for i in range(15):
                    cube.print()
                    cube.rotate_face(move)
                    print("\033c", end="")
                    time.sleep(0.1)

    def solve(self, max_depth):
        # Check if the cube is already solved
        if self.is_win():
            return []

        # Generate all possible moves
        all_moves = ["U", "D", "L", "R", "F", "B"]

        # Initialize the queue for BFS
        queue = deque([(self, [])])

        # Run BFS
        while queue:
            current_cube, current_moves = queue.popleft()

            # If the maximum depth is reached, return None
            if len(current_moves) == max_depth:
                continue

            # Try all possible moves
            for move in all_moves:
                # Create a new cube and apply the move
                new_cube = Cube()
                new_cube.faces = [Face(face.cells) for face in current_cube.faces]
                new_cube.rotate_face(move)

                # If the new cube is solved, return the moves
                if new_cube.is_win():
                    return current_moves + [move]

                # Add the new cube and the moves to the queue
                queue.append((new_cube, current_moves + [move]))

        # If no solution is found, return None
        return None


if __name__ == "__main__":
    moves = ("U", "D", "L", "R", "F", "B")
    scramble_amount = 1
    cube = Cube().scramble(scramble_amount)
    cube.print()
    print(f"Scrambled {scramble_amount} times.")
    solution = cube.solve(6)
    print(f"Solution: {solution}")
    # cube.print()
