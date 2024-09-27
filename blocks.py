from pygame import draw
import styleSheet as Style


class Blocks:
    added_blocks = set()
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

    def draw(self):
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

    def update_cords(self, dx, dy):
        self.x -= dx
        self.y -= dy
        self.is_visible = Blocks.scope_check(self.x, self.y)
        self.set_cords()

    def capture_check(self, x, y):
        return self.x <= x <= (self.x + self.size[0]) and self.y <= y <= (self.y + self.size[1])

    def set_cords(self):
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

    @staticmethod
    def update_all_cords(dx, dy):
        for block in Blocks.added_blocks:
            block.update_cords(dx, dy)

    @staticmethod
    def blocks_capture(pos):
        x, y = pos
        for block in Blocks.added_blocks:
            if block.capture_check(x, y):
                return block, block.showcase
        return None

    @staticmethod
    def set_available_cords(available):
        Blocks.available_zone = available

    @staticmethod
    def scope_check(x, y):
        return Blocks.available_zone[0] <= x <= Blocks.available_zone[2] and \
            Blocks.available_zone[1] <= y <= Blocks.available_zone[3]

    @staticmethod
    def block_button(win, win_size):
        for block_id in range(1, 8):
            block = Blocks(win_size[0] * 0.03, 70 * block_id, win, win_size, block_id, False)
            block.draw()

    @staticmethod
    def generate_block(user_cords, win, win_size, block_id):
        block = Blocks(*user_cords, win, win_size, block_id)
        block.draw()

    @staticmethod
    def update():
        for block in Blocks.added_blocks:
            block.draw()