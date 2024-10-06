from pygame import draw
import styleSheet as Style


class ConnectorRings:
    win = None
    active_ring = None  # visible rings objects
    rings = set()  # all rings objects
    available_zone = None

    def __init__(self, r, zone):
        self.radius = r
        self.cords = None

        self.visible = [0, 0, 0, 0]
        self.active = False

        ConnectorRings.rings.add(self)
        ConnectorRings.available_zone = (zone[0] + self.radius, zone[1] + self.radius,
                                         zone[2] - self.radius, zone[3] - self.radius)

    def draw(self) -> None:
        if self.active:
            for vs, pos in zip(self.visible, self.cords):
                if not vs:
                    continue
                draw.circle(ConnectorRings.win, Style.BLUE, pos, self.radius, 2)

    def hide(self) -> None:
        self.active = False
        self.visible = [0, 0, 0, 0]

    def set_cords(self, cords, visible) -> None:
        self.cords = cords
        if not visible:
            self.hide()
        self.scope_check()

    def switch_visible_rings(self) -> bool:
        """
        Change visibility of connection rings on canvas
        """

        self.active = not self.active
        ConnectorRings.active_ring = None
        if self.active:
            self.scope_check()
            ConnectorRings.active_ring = self

        return self.active

    def scope_check(self) -> None:
        """
        Checking of available zone intersection
        """
        for i in range(4):
            x, y = self.cords[i]
            self.visible[i] = (ConnectorRings.available_zone[0] <= x <= ConnectorRings.available_zone[2] and
                               ConnectorRings.available_zone[1] <= y <= ConnectorRings.available_zone[3])

    def capture_check(self, x, y) -> int | None:
        """
        Check if mouse click by this block
        :param x: mouse x click
        :param y: mouse y click
        :return:
        """
        for i in range(4):
            rx, ry = self.cords[i]
            if abs(x - rx) <= self.radius and abs(y - ry) <= self.radius:
                return i
        return None

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_win(win):
        ConnectorRings.win = win


class ConnectLine:
    pass


class Text:
    win = None

    def __init__(self, text, pos, block_size):
        self.string = text
        self.render = None
        self.rendering()
        self.block_size = block_size
        self.x_offset = self.calculate_x_offset()
        self.y_offset = self.block_size[1] // 3
        self.x = pos[0] + self.x_offset
        self.y = pos[1] + self.y_offset
        self.visible = True

    def draw(self):
        if self.visible:
            Text.win.blit(self.render, (self.x, self.y))

    def update_cords(self, dx, dy, visible):
        self.x -= dx
        self.y -= dy
        self.visible = visible

    def calculate_x_offset(self) -> int:
        return (self.block_size[0] - (self.render.get_width())) // 2

    def add_litter(self, litter):
        self.string += litter
        last_len = self.render.get_width()
        self.rendering()
        self.x += (last_len - self.render.get_width())/2

    def rendering(self):
        self.render = Style.FONT.render(self.string, True, Style.BLACK)

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_win(win):
        Text.win = win

    @staticmethod
    def get_basic_text(block_num) -> tuple:
        match block_num:
            case 1:
                return "Начало",
            case 2:
                return "", "да", "нет"
        return "",


class Blocks:
    added_blocks = set()
    size_rings = set()

    added_blocks_num = 0
    available_zone = None

    def __init__(self, x, y, win, win_size, block_type):
        # 1 - start; 2 - funk; 3 - if; 4 - out_funk; 5 - linker; 6 - for; 7 - stdin

        self.window = win
        self.win_size = win_size
        self.block_type = block_type

        ConnectorRings.set_win(self.window)
        self.connector_rings = ConnectorRings(win_size[1] // 150, Blocks.available_zone)
        self.used_sides = [0, 0, 0, 0]

        self.skale = 1
        self.x, self.y = x, y
        self.size = (self.win_size[0] // 10, self.win_size[1] // 15)
        self.cords, self.cords2 = (0, 0, 0, 0), (0, 0, 0, 0)
        self.set_cords(self.get_cords(self.x, self.y, self.size, self.skale, self.block_type))
        self.visible = True

        Text.set_win(self.window)
        text = Text.get_basic_text(self.block_type)
        self.edit_mode = False
        self.text = Text(text[0], (self.x, self.y), self.size)
        self.add_text = ()

        Blocks.added_blocks.add(self)
        Blocks.added_blocks_num += 1

    # ------------------------------------------------------------------------------------------------------

    def draw(self) -> None:
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

        self.connector_rings.draw()
        self.text.draw()
        for text in self.add_text:
            text.draw()

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

        self.text.update_cords(dx, dy, self.visible)
        self.connector_rings.set_cords(
            ((self.x + self.size[0] // 2, self.y + self.size[1] + self.size[1] // 5),
             (self.x + self.size[0] // 2, self.y - self.size[1] // 5),
             (self.x + self.size[0] + self.size[1] // 5, self.y + self.size[1] // 2),
             (self.x - self.size[1] // 5, self.y + self.size[1] // 2)),
            self.visible
        )

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

    def add_litter(self, litter):
        self.text.add_litter(chr(litter))

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
    def connect_ring_capture(pos) -> (object | None):
        """
        Check all blocks for capturing
        :param pos: (click.x, click.y)
        :return: block id if find None else
        """
        x, y = pos
        if ConnectorRings.active_ring is not None:
            return ConnectorRings.active_ring.capture_check(x, y)
        return None

    @staticmethod
    def set_available_zone(available) -> None:
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

    @staticmethod
    def disable_all_editing() -> None:
        """
        Disable all text editing
        :return: None
        """
        for block in Blocks.added_blocks:
            block.editing = False
