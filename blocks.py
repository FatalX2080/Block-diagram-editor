import pygame
import styleSheet as sst


class Blocks:
    added_blocks = set()

    def __init__(self, x, y, win, win_size, block_type):
        # 1 - start; 2 - funk; 3 - if; 4 - out_funk; 5 - linker; 6 - for; 7 - stdin
        self.window = win
        self.win_size = win_size
        self.block_type = block_type

        self.skale = 1
        self.x, self.y = x, y
        self.size = (self.win_size[0] // 15, self.win_size[1] // 15)
        self.cords, self.cords2 = (0, 0, 0, 0), (0, 0, 0, 0)
        self.is_visible = True
        self.set_cords()

        Blocks.added_blocks.add(self)

    def draw(self):
        if self.is_visible:
            match self.block_type:
                case 1:
                    for rect_data in ((sst.WHITE, 0), (sst.BLACK, 1)):
                        pygame.draw.rect(self.window, rect_data[0], self.cords, rect_data[1], 10)
                case 2:
                    for rect_data in ((sst.WHITE, 0), (sst.BLACK, 1)):
                        pygame.draw.rect(self.window, rect_data[0], self.cords, rect_data[1])
                case 4:
                    for rect_data in ((sst.WHITE, 0), (sst.BLACK, 1)):
                        pygame.draw.rect(self.window, rect_data[0], self.cords, rect_data[1])
                    pygame.draw.rect(self.window, sst.BLACK, self.cords2, 1)
                case 5:
                    for rect_data in ((sst.WHITE, 0), (sst.BLACK, 1)):
                        pygame.draw.circle(self.window, rect_data[0], *self.cords, rect_data[1])
                case _:
                    pygame.draw.polygon(self.window, sst.WHITE, self.cords)
                    pygame.draw.lines(self.window, sst.BLACK, True, self.cords, 1)

    def update_cords(self, dx, dy):
        self.x -= dx
        self.y -= dy
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
                return block
        return None
