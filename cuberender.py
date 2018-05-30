""" Takes cube objects and formats them for rendering """
import math
import lab_utils as lu
from cube import SquareColor

SPACING = 0.05


class CubeRenderer:
    """ Breaks the Cube down into squares and colours to be drawn """

    def __init__(self, cube):
        self.cube = cube

    def get_colors(self):
        """ Gets the list of square colors """
        colors = []
        colors.extend([square.value for square in self.cube.front.squares])
        colors.extend([square.value for square in self.cube.top.squares])
        colors.extend([square.value for square in self.cube.right.squares])
        colors.extend([square.value for square in self.cube.back.squares])
        colors.extend([square.value for square in self.cube.bottom.squares])
        colors.extend([square.value for square in self.cube.left.squares])
        colors.extend([SquareColor.BLACK.value for i in range(4 * 3)])
        return colors

    def get_squares(self):
        """ Gets a list of squares to draw """
        squares = []
        self.__add_front_squares(squares)
        self.__add_top_squares(squares)
        self.__add_right_squares(squares)
        self.__add_back_squares(squares)
        self.__add_bottom_squares(squares)
        self.__add_left_squares(squares)
        CubeRenderer.__make_inner_squares(squares)
        return squares

    def get_normals(self):
        norms = []
        # front
        norms.extend([[0.0, 0.0, -1.0] for _ in range(9)])
        # top
        norms.extend([[0.0, 1.0, 0.0] for _ in range(9)])
        # right
        norms.extend([[1.0, 0.0, 0.0] for _ in range(9)])
        # back
        norms.extend([[0.0, 0.0, 1.0] for _ in range(9)])
        # bottom
        norms.extend([[0.0, -1.0, 0.0] for _ in range(9)])
        # left
        norms.extend([[-1.0, 0.0, 0.0] for _ in range(9)])

        norms.extend([[0.0, 0.0, 1.0] for _ in range(2)])
        norms.extend([[0.0, 0.0, -1.0] for _ in range(2)])
        norms.extend([[0.0, -1.0, 0.0] for _ in range(2)])
        norms.extend([[0.0, 1.0, 0.0] for _ in range(2)])
        norms.extend([[-1.0, 0.0, 0.0] for _ in range(2)])
        norms.extend([[1.0, 0.0, 0.0] for _ in range(2)])
        return norms

    def __add_front_squares(self, squares):
        translation = lambda row, col: lu.make_translation(SPACING + col, SPACING + (2 - row), -SPACING)
        CubeRenderer.__add_squares(self.cube.front.squares, squares, lu.Mat4(),
                                   translation)

    def __add_top_squares(self, squares):
        translation = lambda row, col: lu.make_translation(SPACING + col, 3 - SPACING, -SPACING - 2 + row)
        rot_tfm = lu.make_rotation_x(-math.pi / 2)
        CubeRenderer.__add_squares(self.cube.top.squares, squares, rot_tfm,
                                   translation)

    def __add_right_squares(self, squares):
        translation = lambda row, col: lu.make_translation(3 - SPACING, 2 - row + SPACING, -SPACING - col)
        rot_tfm = lu.make_rotation_y(math.pi / 2)
        CubeRenderer.__add_squares(self.cube.right.squares, squares, rot_tfm,
                                   translation)

    def __add_back_squares(self, squares):
        translation = lambda row, col: lu.make_translation(SPACING + 2 - col, SPACING + (2 - row), -3 + SPACING)
        CubeRenderer.__add_squares(self.cube.front.squares, squares, lu.Mat4(),
                                   translation)

    def __add_bottom_squares(self, squares):
        translation = lambda row, col: lu.make_translation(SPACING + col, SPACING, -SPACING - row)
        rot_tfm = lu.make_rotation_x(-math.pi / 2)
        CubeRenderer.__add_squares(self.cube.top.squares, squares, rot_tfm,
                                   translation)

    def __add_left_squares(self, squares):
        translation = lambda row, col: lu.make_translation(SPACING, 2 - row + SPACING, -SPACING - 2 + col)
        rot_tfm = lu.make_rotation_y(math.pi / 2)
        CubeRenderer.__add_squares(self.cube.right.squares, squares, rot_tfm,
                                   translation)

    @staticmethod
    def __add_squares(squares_in, squares_out, rot_tfm, translation):
        base_rect = make_rect(1 - 2 * SPACING, 1 - 2 * SPACING)
        for i in range(len(squares_in)):
            col = i % 3
            row = int(i / 3)
            trans_tfm = translation(row, col)
            tfm = trans_tfm * rot_tfm
            squares_out.extend(apply_rect_transform(base_rect, tfm))

    @staticmethod
    def __add_inner_squares(squares_out, rot_tfm, translation):
        base_rect = make_rect(3 - 2 * SPACING, 3 - 2 * SPACING)
        for i in range(2):
            trans_tfm = translation(i)
            tfm = trans_tfm * rot_tfm
            squares_out.extend(apply_rect_transform(base_rect, tfm))

    @staticmethod
    def __make_inner_squares(squares):
        """ Makes the inner squares of the cube """
        CubeRenderer.__make_inner_squares_front(squares)
        CubeRenderer.__make_inner_squares_up(squares)
        CubeRenderer.__make_inner_squares_right(squares)

    @staticmethod
    def __make_inner_squares_front(squares):
        rot_tfm = lu.Mat4()
        translation = lambda i: lu.make_translation(SPACING, SPACING, -1 - SPACING - i)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)
        translation = lambda i: lu.make_translation(SPACING, SPACING, -1 + SPACING - i)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)

    @staticmethod
    def __make_inner_squares_up(squares):
        rot_tfm = lu.make_rotation_x(-math.pi / 2)
        translation = lambda i: lu.make_translation(SPACING, 1 - SPACING + i, -SPACING)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)
        translation = lambda i: lu.make_translation(SPACING, 1 + SPACING + i, -SPACING)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)

    @staticmethod
    def __make_inner_squares_right(squares):
        rot_tfm = lu.make_rotation_y(math.pi / 2)
        translation = lambda i: lu.make_translation(1 - SPACING + i, SPACING, -SPACING)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)
        translation = lambda i: lu.make_translation(1 + SPACING + i, SPACING, -SPACING)
        CubeRenderer.__add_inner_squares(squares, rot_tfm, translation)


def make_rect(width, height):
    """ Makes a rectangle on x-y plane to be drawn with GL_TRIANGLES_FAN """
    return [[0, 0, 0], [0, height, 0], [width, height, 0], [width, 0, 0]]


def apply_rect_transform(rect, transform):
    """ Rotates rectangle vertices on given axes """
    return [lu.transformPoint(transform, vert) for vert in rect]