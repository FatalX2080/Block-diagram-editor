from pygame import draw
import styleSheet as Style


class ConnectorRings:
    def __init__(self, r, visible=False):
        self.radius = r
        self.visible = visible

    @staticmethod
    def connectors_capture(pos) -> (tuple | None):
        """
        Check all blocks for capturing
        :param pos: (click.x, click.y)
        :return: connector + block id if find None else
        """
        x, y = pos

        for ring in Blocks.line_rings:
            if ring.capture_check(x, y):
                return ()
        return None


class Blocks:
    added_blocks = set()
    line_rings = set()
    size_rings = set()

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
        self.set_cords(self.get_cords(self.x, self.y, self.size, self.skale, self.block_type))
        self.is_visible = True

        self.connector_rings = ConnectorRings(win_size[1] // 150)

        Blocks.added_blocks.add(self)
        Blocks.added_blocks_num += 1

    # ------------------------------------------------------------------------------------------------------

    def draw(self) -> None:
        """
        Draw bloock on canvas
        :return: None
        """
        if self.is_visible:
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

        if self.is_visible_rings:
            for cords in self.line_rings_cords:
                draw.circle(self.window, Style.BLUE, cords, self.rings_radius, 2)

    def update_cords(self, dx, dy) -> None:
        """
        Update cords of this block
        :param dx: delta x
        :param dy: delta y
        :return: None
        """
        self.x -= dx
        self.y -= dy
        self.is_visible = self.scope_check()

        new_cords = self.get_cords(self.x, self.y, self.size, self.skale, self.block_type)
        self.set_cords(new_cords)

    def capture_check(self, x, y) -> bool:
        """
        Check if mouse click by this block
        :param x: mouse x click
        :param y: mouse y click
        :return:
        """
        return self.x <= x <= (self.x + self.size[0]) and self.y <= y <= (self.y + self.size[1])

    def set_cords(self, t_cords) -> None:
        """
        Set cords of figure
        :param t_cords: tuple(cords; cords2)
        :return: None
        """

        self.line_rings_cords = ((self.x + self.size[0] // 2, self.y + self.size[1] + self.size[1] // 5),
                                 (self.x + self.size[0] // 2, self.y - self.size[1] // 5),
                                 (self.x + self.size[0] + self.size[1] // 5, self.y + self.size[1] // 2),
                                 (self.x - self.size[1] // 5, self.y + self.size[1] // 2))
        self.cords = t_cords[0]
        self.cords2 = t_cords[1]

    def scope_check(self) -> bool:
        """
        Checking of available zone intersection
        :return: **bool** - is in an accessible area
        """
        return Blocks.available_zone[0] <= self.x and \
            (self.x + self.size[0]) <= Blocks.available_zone[2] and \
            Blocks.available_zone[1] <= self.y and \
            (self.y + self.size[1]) <= Blocks.available_zone[3]

    def switch_visible_rings(self) -> None:
        """
        Change visibility of connection rings on canvas
        """
        self.is_visible_rings = not self.is_visible_rings
        Blocks.line_rings = self.line_rings_cords

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_cords(x, y, size, k, block_type) -> tuple:
        """
        Change **self.cords** points of figure (square, oval, ...)
        :return: tuple(cords; cords2)
        """
        x_size, y_size = size
        cords, cords2 = None, None

        match block_type:
            case 3:
                cords = (
                    (x, y + (k * y_size / 2)),
                    (x + k * x_size / 2, y),
                    (x + x_size * k, y + k * y_size / 2),
                    (x + k * x_size / 2, y + y_size)
                )
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
    def set_available_cords(available) -> None:
        """
        Set an available zone for blocks (canvas cords)
        :param available:  tuple[4]
        :return: None
        """
        Blocks.available_zone = available

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
