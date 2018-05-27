""" Rubik's Cube model module """
import enum
import os

class CubeTurn(enum.Enum):
    R = 1
    L = 2
    F = 3
    B = 4
    U = 5
    D = 6

class CubeMove:
    """ Represents a move """
    def __init__(self, turn, turns=1):
        self.turn = turn
        self.turns = turns

class SquareColor(enum.Enum):
    WHITE = 1
    YELLOW = 2
    RED = 3
    ORANGE = 4
    GREEN = 5
    BLUE = 6

def rotate_indices(array, indices):
    first = indices[0]
    old = array[first]
    for i in indices[1:]:
        next_old = array[i]
        array[i] = old
        old = next_old
    array[first] = old

def rotate_faces(faces):
    old = faces[0].squares
    for face in faces[1:]:
        next_old = face.squares
        face.squares = old
        old = next_old
    faces[0] = old

def rotate_on_faces(faces, indices):
    for i in indices:
        first_face = faces[0]
        old = first_face[i]
        for face in faces[1:]:
            next_old = face[i]
            face[i] = old
            old = next_old
        first_face[i] = old

def hard_face_rotations(faces, indices_list):
    faces = [i.squares for i in faces]
    for square_i in range(3):
        indices = [il[square_i] for il in indices_list]
        first = faces[0]
        old = first[indices[0]]
        for i, face in enumerate(faces[1:]):
            next_old = face[indices[i + 1]]
            face[indices[i + 1]] = old
            old = next_old
        first[indices[0]] = old

class Face:
    """ Represents a single face of a Rubik's cube """
    def __init__(self, squares):
        self.squares = squares
    
    def rotate(self, n=1):
        """ Performs a 90 deg clockwise rotation of the face """
        # perform on copy of state, so isn't ruined if error occurs
        squares = self.squares.copy()
        for _ in range(n):
            # perform the rotation
            corners = [0, 2, 8, 6]
            edges = [1, 5, 7, 3]
            rotate_indices(squares, corners)
            rotate_indices(squares, edges)
            # set the new state
            self.squares = squares

    def __str__(self):
        """ String representation of cube """
        return "{0} {1} {2}{nl}{3} {4} {5}{nl}{6} {7} {8}".format(*self.squares, nl=os.linesep)

    def copy(self):
        return Face(self.squares.copy())

    @classmethod
    def from_color(cls, color):
        squares = [color for i in range(9)]
        return cls(squares)
#
#                 0 1 2
#                 3 U 5
#                 6 7 8
#
#   0 1 2  0 1 2  0 1 2  0 1 2
#   3 B 5  3 L 5  3 F 5  3 R 5
#   6 7 8  6 7 8  6 7 8  6 7 8
#
#                 0 1 2
#                 3 D 5
#                 6 7 8

class Cube:
    """ The Rubik's cube model """
    def __init__(self):
        self.top = Face.from_color(SquareColor.YELLOW)
        self.bottom = Face.from_color(SquareColor.WHITE)
        self.front = Face.from_color(SquareColor.RED)
        self.back = Face.from_color(SquareColor.ORANGE)
        self.left = Face.from_color(SquareColor.BLUE)
        self.right = Face.from_color(SquareColor.GREEN)

    def make_move(self, move_name):
        """ Given a string representing a move, make the move """
        pass

    @staticmethod
    def perform_move(side, faces, indices):
        side.rotate()
        faces = [i.squares for i in faces]
        rotate_on_faces(faces, indices)
    
    def move_r(self):
        """ Makes an 'R' move """
        self.right.rotate()
        faces = [self.front, self.top, self.back, self.bottom]
        indices_list = [
            [2, 5, 8],
            [2, 5, 8],
            [6, 3, 0],
            [2, 5, 8]
        ]
        hard_face_rotations(faces, indices_list)

    def move_l(self):
        """ Makes an 'L' move """
        self.left.rotate()
        faces = [self.front, self.bottom, self.back, self.top]
        indices_list = [
            [0, 3, 6],
            [0, 3, 6],
            [8, 5, 2],
            [0, 3, 6]
        ]
        hard_face_rotations(faces, indices_list)

    def move_u(self):
        """ Makes an 'U' move """
        faces = [self.front, self.left, self.back, self.right]
        indices = [0, 1, 2]
        Cube.perform_move(self.top, faces, indices)

    def move_d(self):
        """ Makes an 'D' move """
        faces = [self.front, self.right, self.back, self.left]
        indices = [6, 7, 8]
        Cube.perform_move(self.bottom, faces, indices)

    def move_f(self):
        """ Makes an 'F' move """
        # more complicated than above movements
        # indices changed are different for each face
        self.front.rotate()
        faces = [self.top, self.right, self.bottom, self.left]
        indices_list = [
            [6, 7, 8],
            [0, 3, 6],
            [2, 1, 0],
            [8, 5, 2]
        ]
        hard_face_rotations(faces, indices_list)

    def move_b(self):
        """ Makes an 'B' move """
        # more complicated than above movements
        # indices changed are different for each face
        self.back.rotate()
        faces = [self.top, self.left, self.bottom, self.right]
        indices_list = [
            [0, 1, 2],
            [6, 3, 0],
            [8, 7, 6],
            [2, 5, 8]
        ]
        hard_face_rotations(faces, indices_list)

    def rotate_x(self):
        """ Performs an 'x' rotation """
        self.right.rotate()
        self.left.rotate(3)
        new_top = self.front.copy()
        self.front = self.bottom.copy()
        self.bottom = self.back.copy()
        self.bottom.rotate(2)
        self.back = self.top.copy()
        self.back.rotate(2)
        self.top = new_top
    
    def rotate_y(self):
        """ Performs an 'y' rotation """
        self.top.rotate()
        self.bottom.rotate(3)
        new_left = self.front.copy()
        self.front = self.right.copy()
        self.right = self.back.copy()
        self.back = self.left.copy()
        self.left = new_left


    def rotate_z(self):
        """ Performs an 'z' rotation """
        self.front.rotate()
        self.back.rotate(3)
        new_right = self.top.copy()
        self.top = self.left.copy()
        self.top.rotate()
        self.left = self.bottom.copy()
        self.left.rotate()
        self.bottom = self.right.copy()
        self.bottom.rotate()
        self.right = new_right
        self.right.rotate()
    
    def __str__(self):
        """ String representation of cube """
        return "Top:{nl}{0}{nl}Front:{nl}{1}{nl}Left:{nl}{2}{nl}Right:{nl}{3}{nl}\
Bottom:{nl}{4}{nl}Back:{nl}{5}{nl}".format(
            self.top, self.front, self.left, self.right, self.bottom,
            self.back, nl=os.linesep
        )

if __name__ == "__main__":
    c = Cube()
    c.move_r()
    c.move_f()
    c.move_u()
    c.rotate_z()
    print(c)