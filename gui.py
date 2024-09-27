from blocks import Blocks
import styleSheet as Style

import pygame
import sys
from math import ceil
import numpy as np


class TabPosition:
    """
    Class of pygame.win tabs cords
    """

    def __init__(self, window_size):
        ws = window_size

        self.window_size = ws
        self.main_bg = (0, ws[1] * 0.05, ws[0] * 0.98, ws[1] * 0.90)
        self.objects_block = (ws[0] * 0.004, ws[1] * 0.06, ws[0] * 0.15, ws[1] * 0.88)
        self.canvas_size = (ws[0] * 0.818, ws[1] * 0.88)
        self.canvas = (2 * self.objects_block[0] + self.objects_block[2], ws[1] * 0.06,
                       self.canvas_size[0], self.canvas_size[1])
        self.info_block = (self.canvas[0] + self.canvas_size[0] - ws[0] * 0.144,
                           self.canvas[1] + ws[1] * 0.004, ws[0] * 0.14, ws[1] * 0.38)


class Canvas:
    """
    Class of pygame.win canvas
    """

    def __init__(self, cnv_cords, win, tab_sizes):
        self.user_cords = [10e4, 10e4]

        self.tab_sizes = tab_sizes
        self.canvas_cords = (cnv_cords[0], cnv_cords[1], cnv_cords[0] + cnv_cords[2],
                             cnv_cords[1] + cnv_cords[3])
        self.win = win
        self.grid_step = 15

    def capture_check(self, pos) -> bool:
        return self.canvas_cords[0] <= pos[0] <= self.canvas_cords[2] and \
            self.canvas_cords[1] <= pos[1] <= self.canvas_cords[2]

    def update_cord(self, dx, dy) -> None:
        self.user_cords[0] += dx
        self.user_cords[1] += dy

    def grid_update(self) -> None:
        hf_step = self.grid_step // 2 + 1

        pygame.draw.rect(self.win, Style.WHITE, self.tab_sizes.canvas)
        pygame.draw.rect(self.win, Style.DARK_GRAY, self.tab_sizes.canvas, 1)

        relative_cords = (self.user_cords[0] - (self.canvas_cords[0] / 2),
                          self.user_cords[1] - (self.canvas_cords[1] / 2))

        net_start_point = [self.canvas_cords[_] + ceil(
            relative_cords[_] / self.grid_step) * self.grid_step - relative_cords[_] for _ in (0, 1)]

        grid_cords = [np.arange(
            net_start_point[_] + hf_step, self.canvas_cords[2 + _] - self.grid_step, self.grid_step
        ) for _ in (0, 1)]

        for x in grid_cords[0]:
            for y in grid_cords[1]:
                pygame.draw.circle(self.win, Style.BLACK, (x, y), 1)

    def info_block_update(self):
        # Информационный блок
        x = int(self.user_cords[0] - 10e4)
        y = int(self.user_cords[1] - 10e4)
        text_raws = [f"X: {x} {' ' * (12 - len(str(x)))} Y: {y}",
                     f"Block: {Blocks.added_blocks_num}"]

        pygame.draw.rect(self.win, Style.WHITE, self.tab_sizes.info_block)
        pygame.draw.rect(self.win, Style.DARK_GRAY, self.tab_sizes.info_block, 1)

        x_text = self.tab_sizes.info_block[0] + self.tab_sizes.window_size[0] * 0.006
        y_text = self.tab_sizes.info_block[1] + self.tab_sizes.window_size[1] * 0.007
        delta_y = self.tab_sizes.window_size[1] * 0.025

        for raw_id in range(len(text_raws)):
            self.win.blit(Style.FONT.render(text_raws[raw_id], True, Style.BLACK), (
                x_text, y_text + delta_y * raw_id
            ))


class Gui:
    """
    Main ide class
    """

    def __init__(self, win_size=(1280, 720), fps=30):
        pygame.init()
        self.running = True
        self.win_size = win_size

        self.canvas_capture = False
        self.captured_block = (None, None)
        self.last_mouse_pos = (0, 0)

        self.win = pygame.display.set_mode(self.win_size)
        self.tab_sizes = TabPosition(self.win_size)
        self.canvas = Canvas(self.tab_sizes.canvas, self.win, self.tab_sizes)
        Blocks.set_available_cords(self.canvas.canvas_cords)

        self.win.fill((255, 255, 255))
        self.__initial_gui_rendering()
        pygame.time.Clock().tick(fps)

    def mainloop(self) -> None:
        while self.running:
            self.__event_update()
            self.__rendering()

    # ------------------------------------------------------------------------------------------------------

    def __initial_gui_rendering(self) -> None:
        pygame.draw.rect(self.win, Style.GRAY, self.tab_sizes.main_bg)
        pygame.draw.rect(self.win, Style.WHITE, self.tab_sizes.objects_block)
        pygame.draw.rect(self.win, Style.DARK_GRAY, self.tab_sizes.objects_block, 1)
        Blocks.block_button(self.win, self.win_size)

    def __rendering(self) -> None:
        self.canvas.grid_update()
        Blocks.update()
        self.canvas.info_block_update()
        pygame.display.flip()

    # ------------------------------------------------------------------------------------------------------

    def __event_update(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.MOUSEBUTTONDOWN:
                    self.__event_mousedown(event)
                case pygame.MOUSEMOTION:
                    self.__event_mousemove(event)
                case pygame.MOUSEBUTTONUP:
                    self.__event_mouseup(event)

    def __event_mousedown(self, event) -> None:
        if event.button == 1:
            capture_obg = Blocks.blocks_capture(event.pos)
            if capture_obg[0] is not None:
                if capture_obg[1]:
                    self.captured_block = capture_obg
                    self.last_mouse_pos = event.pos
                else:
                    cords = (self.canvas.canvas_cords[0] + self.win_size[0] * 0.04,
                             self.canvas.canvas_cords[1] + self.win_size[1] * 0.04)
                    Blocks.generate_block(
                        cords, self.win, self.win_size, capture_obg[0].block_type
                    )
            elif self.canvas.capture_check(event.pos):
                self.canvas_capture = True
                self.last_mouse_pos = event.pos

    def __event_mousemove(self, event) -> None:
        dx, dy = [self.last_mouse_pos[_] - event.pos[_] for _ in (0, 1)]

        if self.canvas_capture:
            self.canvas.update_cord(dx, dy)
            Blocks.update_all_cords(dx, dy)
        elif self.captured_block[0] is not None:
            self.captured_block[0].update_cords(dx, dy)

        self.last_mouse_pos = event.pos

    def __event_mouseup(self, event) -> None:
        self.canvas_capture = False
        self.captured_block = (None, None)
        self.last_mouse_pos = event.pos
