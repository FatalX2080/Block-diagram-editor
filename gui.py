from math import ceil
from sys import exit
from time import time

import numpy as np
import pygame

import styleSheet as Style
from blocks import Blocks
from blocks_parts.connect_lines import Lines as Cl
from blocks_parts.connector_rings import ConnectorRings as Cr
from blocks_parts.text import Texts as Tx


class TabPosition:
    """
    Class of pygame.win tabs cords
    """

    def __init__(self, window_size):
        ws = window_size

        self.window_size = ws
        self.main_bg = (0, ws[1] * 0.05, ws[0] * 0.98, ws[1] * 0.90)
        self.objects_block = (ws[0] * 0.004, ws[1] * 0.06, ws[0] * 0.15, ws[1] * 0.88)
        self.blocks = (
            (ws[0] * 0.03, ws[0] * 0.005),
            (ws[0] * 0.18, ws[1] * 0.885),
            ws[1] * 0.1,
            (ws[0] // 10, ws[1] // 15)
        )  # x, y, dy, size
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


class BlocksTab:
    def __init__(self, blocks_size):
        self.blocks_size = blocks_size
        self.spawn_queue = None

    def click_check(self, pos) -> bool:
        if not (self.blocks_size[0][0] * 1.2 <= pos[0] <= self.blocks_size[1][0] * 0.8 and
                self.blocks_size[0][1] <= pos[1] <= 8 * self.blocks_size[2]):
            return False
        self.spawn_queue = pos[1] // self.blocks_size[2]
        return True


class Gui:
    """
    Main ide class
    """

    def __init__(self, win_size=(1280, 720), fps=30):
        pygame.init()
        self.running = True
        self.win_size = win_size

        self.canvas_capture = False
        self.active_block = None
        self.last_block = None
        self.text_block = None
        self.active_connector = (None, None)
        self.last_connector = (None, None)
        self.line_active = False
        self.last_mouse_pos = (0, 0)
        self.last_click_time = time()

        self.win = pygame.display.set_mode(self.win_size)
        self.tab_sizes = TabPosition(self.win_size)
        self.canvas = Canvas(self.tab_sizes.canvas, self.win, self.tab_sizes)
        self.block_tab = BlocksTab(self.tab_sizes.blocks)

        Blocks.put_dependencies_window(self.win)
        Blocks.set_available_zone(win_size, self.canvas.canvas_cords)

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

        x, y = self.tab_sizes.blocks[0]
        y_offset = self.tab_sizes.blocks[2]
        size = self.tab_sizes.blocks[3]

        for block_id in range(1, 8):
            cords = list(Blocks.get_cords(x, y + y_offset * block_id, size, 1, block_id))

            match block_id:
                case 1:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        pygame.draw.rect(self.win, rect_data[0], cords[0], rect_data[1], 10)
                case 2:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        pygame.draw.rect(self.win, rect_data[0], cords[0], rect_data[1])
                case 4:
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        pygame.draw.rect(self.win, rect_data[0], cords[0], rect_data[1])
                    pygame.draw.rect(self.win, Style.BLACK, cords[1], 1)
                case 5:
                    cords[0][0] += self.win_size[0] * 0.035
                    for rect_data in ((Style.WHITE, 0), (Style.BLACK, 1)):
                        pygame.draw.circle(self.win, rect_data[0], *cords, rect_data[1])
                case _:
                    pygame.draw.polygon(self.win, Style.WHITE, cords[0])
                    pygame.draw.lines(self.win, Style.BLACK, True, cords[0], 1)

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
                    exit()
                case pygame.MOUSEBUTTONDOWN:
                    self.__event_mousedown(event)
                case pygame.MOUSEMOTION:
                    self.__event_mousemove(event)
                case pygame.MOUSEBUTTONUP:
                    self.__event_mouseup(event)
                case pygame.KEYDOWN:
                    self.__event_keydown(event)

    def __event_mousedown(self, event) -> None:
        if event.button == pygame.BUTTON_LEFT:
            self.active_block = Blocks.blocks_capture(event.pos)
            self.text_block = Tx.checking_relevance(self.last_block)
            self.active_connector = Cr.connect_ring_capture(event.pos)  # block; id
            self.last_mouse_pos = event.pos

            if self.active_block and self.last_connector[0]:
                Cl.connect(self.active_block, self.last_connector, event.pos)
                self.active_connector = (None, None)
                self.last_connector = (None, None)

            elif self.active_block and (self.active_block == self.last_block):
                # activation of text editing mode
                self.text_block = self.active_block
                self.active_block.edit_mode = True

            elif self.active_connector[0]:
                # connector pressing test

                # TODO register disabling previous connectors
                self.last_connector = self.active_connector
                self.last_block.conn_rings.switch_visible()
                Cl.create_cnn_line(*self.active_connector, event.pos)

            elif self.canvas.capture_check(event.pos):
                # canvas click test
                if self.last_connector[0]:
                    self.last_connector[0].lines.del_line(self.last_connector[1])
                    self.last_connector = (None, None)
                else:
                    self.canvas_capture = True

            elif self.block_tab.click_check(event.pos):
                # checking clicks on a block bar
                new_cords = (self.win_size[0] * 0.18, self.win_size[1] * 0.08)
                Blocks.generate_block(new_cords, self.win, self.win_size, self.block_tab.spawn_queue)
                self.block_tab.spawn_queue = None

        elif event.button == pygame.BUTTON_RIGHT:
            self.active_block = Blocks.blocks_capture(event.pos)
            if self.active_block:
                self.active_block.conn_rings.switch_visible()

    def __event_mousemove(self, event) -> None:
        dx, dy = [self.last_mouse_pos[_] - event.pos[_] for _ in (0, 1)]

        if self.last_connector[0]:
            Cl.set_cnn_line_epos(*self.last_connector, (dx, dy))
        elif self.active_block is not None:
            self.active_block.update_cords(dx, dy)
        elif self.canvas_capture:
            self.canvas.update_cord(dx, dy)
            Blocks.update_all_cords(dx, dy)
        self.last_mouse_pos = event.pos

    def __event_mouseup(self, event) -> None:
        self.canvas_capture = False
        self.last_block = self.active_block
        self.active_block = None
        self.last_mouse_pos = event.pos
        self.last_click_time = time()

    def __event_keydown(self, event) -> None:
        if self.last_block is not None and self.last_block.edit_mode:
            Tx.update_litter(self.last_block, event.key)
