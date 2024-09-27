from pygame import draw
import styleSheet as Style


class Blocks:
    added_blocks = set()
    added_blocks_num = -7
    available_zone = None

    def __init__(self, x, y, win, win_size, block_type, showcase=True):
        # 1 - start; 2 - funk; 3 - if; 4 - out_funk; 5 - linker; 6 - for; 7 - stdin
        self.window = win
        self.win_size = win_size
        self.block_type = block_type
        self.showcase = showcase

        self.skale = 1
        self.x, self.y = x, y
        self.size = (self.win_size[0] // 10, self.win_size[1] // 15)
        self.cords, self.cords2 = (0, 0, 0, 0), (0, 0, 0, 0)
        self.is_visible = True
        self.set_cords()

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

    def update_cords(self, dx, dy) -> None:
        """
        Update cords of this block
        :param dx: delta x
        :param dy: delta y
        :return: None
        """
        self.x -= dx
        self.y -= dy
        self.is_visible = self.showcase * self.scope_check()
        self.set_cords()

    def capture_check(self, x, y) -> bool:
        """
        Check if mouse click by this block
        :param x: mouse x click
        :param y: mouse y click
        :return:
        """
        return self.x <= x <= (self.x + self.size[0]) and self.y <= y <= (self.y + self.size[1])

    def set_cords(self) -> None:
        """
        Change **self.cords** points of figure (square, oval, ...)
        :return: None
        """
        x, y = self.x, self.y
        x_size, y_size = self.size
        k = self.skale
        match self.block_type:
            case 3:
                self.cords = (
                    (x, y + (k * y_size / 2)),
                    (x + k * x_size / 2, y),
                    (x + x_size * k, y + k * y_size / 2),
                    (x + k * x_size / 2, y + y_size)
                )
            case 4:
                self.cords2 = (x + x_size * 0.1, y, x_size * 0.8, y_size)
                self.cords = (x, y, x_size * k, y_size * k)
            case 5:
                r = self.size[1] / 2 * k
                self.cords = ((x + r, y + r), r)
            case 6:
                self.cords = (
                    (x, y + (k * y_size / 2)),
                    (x + (k * y_size / 2), y),
                    (x + x_size - (k * y_size / 2), y),
                    (x + x_size, y + k * y_size / 2),
                    (x + x_size - (k * y_size / 2), y + y_size),
                    (x + (k * y_size / 2), y + y_size)
                )
            case 7:
                self.cords = (
                    (x + (k * y_size / 2), y),
                    (x + x_size, y),
                    (x + x_size - (k * y_size / 2), y + k * y_size),
                    (x, y + y_size),
                )
            case _:
                self.cords = (x, y, self.size[0] * k, self.size[1] * k)

    def scope_check(self) -> bool:
        """
        Checking of available zone intersection
        :return: **bool** - is in an accessible area
        """
        return Blocks.available_zone[0] <= self.x and \
            (self.x + self.size[0]) <= Blocks.available_zone[2] and \
            Blocks.available_zone[1] <= self.y and \
            (self.y + self.size[1]) <= Blocks.available_zone[3]

    # ------------------------------------------------------------------------------------------------------

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
    def blocks_capture(pos) -> tuple:
        """
        Check all blocks for capturing
        :param pos: (click.x, click.y)
        :return: (block id | block visible mode) if find (None | None) else
        """
        x, y = pos
        for block in Blocks.added_blocks:
            if block.capture_check(x, y):
                return block, block.showcase
        return None, None

    @staticmethod
    def set_available_cords(available) -> None:
        """
        Set an available zone for blocks (canvas cords)
        :param available:  tuple[4]
        :return: None
        """
        Blocks.available_zone = available

    @staticmethod
    def block_button(win, win_size) -> None:
        """
        Generte all blocks as buttons (fix pos and clickable)
        :param win: pygame.window
        :param win_size: tuple of windows size
        :return:
        """
        for block_id in range(1, 8):
            block = Blocks(win_size[0] * 0.03, 70 * block_id, win, win_size, block_id, False)
            block.draw()

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
