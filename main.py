import pygame
import sys, math
import numpy as np

pygame.init()


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
        self.cords = (0, 0, 0, 0)
        self.set_cords()

        Blocks.added_blocks.add(self)

    def draw(self):

        match self.block_type:
            case 1:
                for rect_data in ((Gui.WHITE, 0), (Gui.BLACK, 1)):
                    pygame.draw.rect(self.window, rect_data[0], self.cords, rect_data[1], 10)
            case 2:
                for rect_data in ((Gui.WHITE, 0), (Gui.BLACK, 1)):
                    pygame.draw.rect(self.window, rect_data[0], self.cords, rect_data[1], rect_data[1])
            case 3:
                pygame.draw.polygon(self.window, Gui.WHITE, self.cords)
                pygame.draw.lines(self.window, Gui.BLACK, True, self.cords, 1)

    def update_cords(self, dx, dy):
        self.x -= dx
        self.y -= dy
        self.set_cords()

    def capture_check(self, x, y):
        return self.cords[0] <= x <= (self.cords[0] + self.cords[2]) and \
            self.cords[1] <= y <= (self.cords[1] + self.cords[3])

    def set_cords(self):
        x, y = self.x, self.y
        k = self.skale
        match self.block_type:
            case 3:
                self.cords = ([x, y + (k * self.size[1] / 2)],
                              [x + k * self.size[0] / 2, y],
                              [x + self.size[0] * k, y + k * self.size[1] / 2],
                              [x + k * self.size[0] / 2, y + self.size[1]])
            case _:
                self.cords = (x, y, self.size[0] * k, self.size[1] * k)

    @staticmethod
    def update_all_cords(dx, dy):
        for block in Blocks.added_blocks:
            block.update_cords(dx, dy)

    @staticmethod
    def block_capture(x, y):
        for block in Blocks.added_blocks:
            if block.capture_chack(x, y):
                return block
        return None


class Gui:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (160, 160, 160)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)

    FONT = pygame.font.SysFont(None, 20)

    class TabPosition:
        def __init__(self, window_size):
            ws = window_size

            self.window_size = window_size
            self.main_bg = (0, ws[1] * 0.05, ws[0] * 0.98, ws[1] * 0.90)
            self.objects_block = (ws[0] * 0.004, ws[1] * 0.06, ws[0] * 0.15, ws[1] * 0.88)
            self.canvas_size = (ws[0] * 0.818, ws[1] * 0.88)
            self.canvas = (2 * self.objects_block[0] + self.objects_block[2], ws[1] * 0.06,
                           self.canvas_size[0], self.canvas_size[1]
                           )
            self.info_block = (self.canvas[0] + self.canvas_size[0] - ws[0] * 0.144,
                               self.canvas[1] + ws[1] * 0.004, ws[0] * 0.14, ws[1] * 0.38)

    class Canvas:
        def __init__(self, canvas_cords, win, tab_sizes):
            self.user_cords = [10000, 10000]

            self.tab_sizes = tab_sizes
            self.canvas_cords = (canvas_cords[0], canvas_cords[1],
                                 canvas_cords[0] + canvas_cords[2],
                                 canvas_cords[1] + canvas_cords[3]
                                 )
            self.win = win
            self.grid_step = 15

        def capture_check(self, pos):
            return self.canvas_cords[0] <= pos[0] <= self.canvas_cords[2] and \
                self.canvas_cords[1] <= pos[1] <= self.canvas_cords[2]

        def update_cord(self, dx, dy):
            self.user_cords[0] += dx
            self.user_cords[1] += dy

        def update(self):
            hf_step = self.grid_step // 2 + 1

            pygame.draw.rect(self.win, Gui.WHITE, self.tab_sizes.canvas)
            pygame.draw.rect(self.win, Gui.DARK_GRAY, self.tab_sizes.canvas, 1)

            relative_cords = (self.user_cords[0] - (self.canvas_cords[0] / 2),
                              self.user_cords[1] - (self.canvas_cords[1] / 2))

            net_start_point = [self.canvas_cords[_] + math.ceil(
                relative_cords[_] / self.grid_step) * self.grid_step - relative_cords[_] for _ in (0, 1)]

            grid_cords = [np.arange(
                net_start_point[_] + hf_step, self.canvas_cords[2 + _] - self.grid_step, self.grid_step
            ) for _ in (0, 1)]

            for x in grid_cords[0]:
                for y in grid_cords[1]:
                    pygame.draw.circle(self.win, Gui.BLACK, (x, y), 1)

            # Информационный блок
            x = int(self.user_cords[0] - 10 ** 4)
            y = int(self.user_cords[1] - 10 ** 4)
            text = f"X: {x} {' ' * (12 - len(str(x)))} Y: {y}"
            pygame.draw.rect(self.win, Gui.WHITE, self.tab_sizes.info_block)
            pygame.draw.rect(self.win, Gui.DARK_GRAY, self.tab_sizes.info_block, 1)
            self.win.blit(Gui.FONT.render(text, True, Gui.BLACK), (
                self.tab_sizes.info_block[0] + self.tab_sizes.window_size[0] * 0.006,
                self.tab_sizes.info_block[1] + self.tab_sizes.window_size[1] * 0.006))

    def __init__(self, win_size=(1280, 720), fps=30):
        self.running = True
        self.win_size = win_size

        self.canvas_capture = False
        self.last_click_pos = (0, 0)
        self.win = pygame.display.set_mode(self.win_size)

        self.tab_sizes = self.TabPosition(self.win_size)
        self.canvas = self.Canvas(self.tab_sizes.canvas, self.win, self.tab_sizes)
        self.block1 = Blocks(500, 500, self.win, self.win_size, 3)

        self.win.fill((255, 255, 255))
        self.__initial_gui_rendering()
        pygame.time.Clock().tick(fps)

    def mainloop(self):
        while self.running:
            self.__event_update()
            self.__rendering()

    def __initial_gui_rendering(self):
        # Основной задник
        pygame.draw.rect(self.win, Gui.GRAY, self.tab_sizes.main_bg)

        # Блок блоков
        pygame.draw.rect(self.win, Gui.WHITE, self.tab_sizes.objects_block)
        pygame.draw.rect(self.win, Gui.DARK_GRAY, self.tab_sizes.objects_block, 1)

    def __rendering(self):
        self.canvas.update()
        self.block1.draw()
        pygame.display.flip()

    def __event_update(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.canvas.capture_check(event.pos):
                            self.canvas_capture = True
                            self.last_click_pos = event.pos
                case pygame.MOUSEMOTION:
                    dx, dy = [self.last_click_pos[_] - event.pos[_] for _ in (0, 1)]

                    if self.canvas_capture:
                        self.canvas.update_cord(dx, dy)
                        Blocks.update_all_cords(dx, dy)
                        self.last_click_pos = event.pos
                case pygame.MOUSEBUTTONUP:
                    self.canvas_capture = False
                    self.last_click_pos = event.pos


def main():
    gui.mainloop()


gui = Gui()
if __name__ == "__main__":
    main()
