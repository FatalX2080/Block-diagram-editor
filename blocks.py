from time import time

from pygame import draw

import styleSheet as Style
from blocks_parts.connect_lines import Lines
from blocks_parts.connector_rings import ConnectorRings as Rings
from blocks_parts.text import Texts


class Blocks:
    added_blocks = set()
    added_blocks_num = 0
    available_zone = None

    def __init__(self, x, y, win, win_size, block_type):
        # 1 - start; 2 - funk; 3 - if; 4 - out_funk; 5 - linker; 6 - for; 7 - stdin

        self.window = win
        self.win_size = win_size
        self.block_type = block_type

        self.skale = 1
        self.x, self.y = x, y
        self.size = (self.win_size[0] // 10, self.win_size[1] // 15)
        self.cords, self.cords2 = (0, 0, 0, 0), (0, 0, 0, 0)
        self.visible = True

        self.set_cords(self.get_cords(self.x, self.y, self.size, self.skale, self.block_type))
        self.conn_rings = Rings(self)
        self.texts = Texts(block_type, (self.x, self.y), self.size)
        self.lines = Lines()

        self.last_click_time = time()

        Blocks.added_blocks.add(self)
        Blocks.added_blocks_num += 1

    # ------------------------------------------------------------------------------------------------------

    def draw(self) -> None:
        """
        Draw bloock on canvas with dependence
        :return: None
        """
        self.draw_box()
        self.conn_rings.draw()
        self.lines.draw()
        self.texts.draw()

    def draw_box(self) -> None:
        """
        Draw bloock on canvas
        :return: None
        """
        if self.visible:
            match self.block_type:
                case 1:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        draw.rect(self.window, rect_data[0], self.cords, rect_data[1], 10)
                case 2:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        draw.rect(self.window, rect_data[0], self.cords, rect_data[1])
                case 4:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        draw.rect(self.window, rect_data[0], self.cords, rect_data[1])
                    draw.rect(self.window, Style.BLACK, self.cords2, 1)
                case 5:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        draw.circle(self.window, rect_data[0], *self.cords, rect_data[1])
                case _:
                    draw.polygon(self.window, Style.WHITE, self.cords)
                    draw.lines(self.window, Style.BLACK, True, self.cords, 1)

    def update_cords(self, dx, dy) -> None:
        """
        Update cords of this block
        :param dx: delta x
        :param dy: delta y
        :return: None
        """
        self.x -= dx
        self.y -= dy
        self.visible = self.scope_check()
        self.lines.update_cords(dx, dy)
        self.texts.update_cords(dx, dy, self.visible)
        self.conn_rings.set_cords(self.x, self.y, self.size, self.visible)

        new_cords = self.get_cords(self.x, self.y, self.size, self.skale, self.block_type)
        self.set_cords(new_cords)

    def set_cords(self, t_cords) -> None:
        """
        Set cords of figure
        :param t_cords: tuple(cords; cords2)
        :return: None
        """

        self.cords = t_cords[0]
        self.cords2 = t_cords[1]

    def capture_check(self, x, y) -> bool:
        """
        Check if mouse click by this block
        :param x: mouse x click
        :param y: mouse y click
        :return:
        """
        return self.x <= x <= (self.x + self.size[0]) and self.y <= y <= (self.y + self.size[1])

    def scope_check(self) -> bool:
        """
        Checking of available zone intersection
        :return: **bool** - is in an accessible area
        """
        return Blocks.available_zone[0] <= self.x and \
            (self.x + self.size[0]) <= Blocks.available_zone[2] and \
            Blocks.available_zone[1] <= self.y and \
            (self.y + self.size[1]) <= Blocks.available_zone[3]

    def get_cn_side(self, x, y) -> tuple:
        """
        -------------
        |11111111111|
        |4         2|
        |33333333333|
        -------------
        """
        if self.y <= y <= self.y + self.size[1] * 0.3:
            return 1, [self.x + self.size[0] // 2, self.y]
        elif self.y + self.size[1] * 0.7 <= y <= self.y + self.size[1]:
            return 3, [self.x + self.size[0] // 2, self.y + self.size[1]]
        elif self.x <= x <= self.x + self.size[0] * 0.4:
            return 4, [self.x, self.y + self.size[1] // 2]
        return 2, [self.x + self.size[0], self.y + self.size[1] // 2]

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_cords(x, y, size, k, block_type) -> tuple:
        """
        Calculates block points (square, oval, ...)
        :return: tuple(cords; cords2)
        """
        x_size, y_size = size
        cords, cords2 = None, None

        match block_type:
            case 3:
                cords = [
                    [x, y + (k * y_size / 2)],
                    [x + k * x_size / 2, y],
                    [x + x_size * k, y + k * y_size / 2],
                    [x + k * x_size / 2, y + y_size]
                ]
            case 4:
                cords = (x, y, x_size * k, y_size * k)
                cords2 = (x + x_size * 0.1, y, x_size * 0.8, y_size)
            case 5:
                cords2 = y_size / 2 * k
                cords = [x + cords2, y + cords2]
            case 6:
                cords = (
                    (x, y + (k * y_size / 2)),
                    (x + (k * y_size / 2), y),
                    (x + x_size - (k * y_size / 2), y),
                    (x + x_size, y + k * y_size / 2),
                    (x + x_size - (k * y_size / 2), y + y_size),
                    (x + (k * y_size / 2), y + y_size)
                )
            case 7:
                cords = (
                    (x + (k * y_size / 2), y),
                    (x + x_size, y),
                    (x + x_size - (k * y_size / 2), y + k * y_size),
                    (x, y + y_size),
                )
            case _:
                cords = (x, y, x_size * k, y_size * k)

        return cords, cords2

    @staticmethod
    def update_all_cords(dx, dy) -> None:
        """
        Change cords of all blocks
        :param dx: delta x
        :param dy: del
        :return: None
        """
        for block in Blocks.added_blocks:
            block.update_cords(dx, dy)

    @staticmethod
    def blocks_capture(pos) -> (object | None):
        """
        Check all blocks for capturing
        :param pos: (click.x, click.y)
        :return: block id if find None else
        """
        x, y = pos
        for block in Blocks.added_blocks:
            if block.capture_check(x, y):
                return block
        return None

    @staticmethod
    def generate_block(user_cords, win, win_size, block_id) -> None:
        """
        Adds a new block to the canvas
        :param user_cords: spawn cords
        :param win: pygame.window
        :param win_size: tuple of windows size
        :param block_id: block id number from 1 to 8
        :return: None
        """
        block = Blocks(*user_cords, win, win_size, block_id)
        block.draw()

    @staticmethod
    def update() -> None:
        """
        Redraw all blocks
        :return: None
        """
        for block in Blocks.added_blocks:
            block.draw()

    @staticmethod
    def put_dependencies_window(window) -> None:
        Rings.set_win(window)
        Lines.set_win(window)
        Texts.set_win(window)

    @staticmethod
    def set_available_zone(win_size, available) -> None:
        Blocks.available_zone = available
        radius = win_size[1] // 150
        Rings.radius = radius
        Rings.set_available_zone((available[0] + radius, available[1] + radius,
                                  available[2] - radius, available[3] - radius))
        Lines.set_available_zone((available[0] * 1.05, available[1] * 1.05,
                                  available[2] * 0.97, available[3] * 0.97))
