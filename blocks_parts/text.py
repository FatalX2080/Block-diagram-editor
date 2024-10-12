from time import time

import styleSheet as Style


class Text:
    win = None

    def __init__(self, text, pos, block_size):
        self.string = text
        self.render = None
        self.rendering()

        shape = self.get_shape()
        self.block_size = block_size
        self.x = pos[0] + (self.block_size[0] - shape[0]) / 2
        self.y = pos[1] + (self.block_size[1] - shape[1]) / 2

        self.visible = True

    def draw(self) -> None:
        """
        Display block text on canvas
        """
        if self.visible:
            Text.win.blit(self.render, (self.x, self.y))

    def update_cords(self, dx, dy, visible) -> None:
        """
        Change text position on canvas
        """
        self.x -= dx
        self.y -= dy
        self.visible = visible

    def add_litter(self, litter) -> None:

        self.string += [litter]
        l_width = self.get_shape()[0]
        self.rendering()
        self.x += (l_width - self.get_shape()[0]) / 2

    def pop_litter(self) -> None:
        if self.string:
            self.string.pop()
            l_width = self.get_shape()[0]
            self.rendering()
            self.x += (l_width - self.get_shape()[0]) / 2

    def rendering(self) -> None:
        self.render = Style.FONT.render("".join(self.string), True, Style.BLACK)

    def get_shape(self) -> tuple:
        return self.render.get_width(), self.render.get_height()

    # ------------------------------------------------------------------------------------------------------


class Texts:
    def __init__(self, block_type, block_pos, block_size):
        self.edit_mode = False
        self.block_type = block_type
        self.block_pos = block_pos
        self.block_size = block_size

        # TODO Do normal base text processing
        basic = Texts.get_basic_text(self.block_type)
        self.text_list = [Text(basic[0], (block_pos[0], block_pos[1]), self.block_size)]

    def draw(self):
        for text in self.text_list:
            text.draw()

    def update_cords(self, dx, dy, visible) -> None:
        """
        Change text position on canvas
        """
        for text in self.text_list:
            text.update_cords(dx, dy, visible)

    @staticmethod
    def checking_relevance(block):
        return block if block and (time() - block.last_click_time) else None

    @staticmethod
    def set_win(win):
        Text.win = win

    @staticmethod
    def update_litter(block, litter):
        match litter:
            case 8: 
                block.texts.text_list[0].pop_litter()
            case _:
                block.texts.text_list[0].add_litter(chr(litter))

    @staticmethod
    def get_basic_text(block_num) -> tuple:
        match block_num:
            case 1:
                return list("Начало"),
            case 2:
                return list(""), list("да"), list("нет")
        return list(""),
