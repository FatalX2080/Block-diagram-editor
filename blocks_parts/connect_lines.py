from os import lseek

import styleSheet as Style
from pygame import draw


def minmax(a, b, val):
    """
    a: left border
    b: right border
    """
    return min(max(val, b), a)


class ConnectLines:
    win = None
    available_zone = None

    def __init__(self, spos, epos, width=2):
        self.width = width

        self.start_pos = list(spos)
        self.end_pos = list(epos)
        self.rstart_pos = None
        self.rend_pos = None

        self.set_rendering_cords()

    def draw(self) -> None:
        draw.line(ConnectLines.win, Style.BLACK, self.rstart_pos, self.rend_pos, self.width)

    def update_cords(self, side, dx, dy) -> None:
        match side:
            case 1:
                # end
                self.start_pos[0] -= dx
                self.start_pos[1] -= dy
            case 0:
                # start
                self.end_pos[0] -= dx
                self.end_pos[1] -= dy

        self.set_rendering_cords()

    def set_rendering_cords(self):
        self.rstart_pos = ConnectLines.scope_check(self.start_pos)
        self.rend_pos = ConnectLines.scope_check(self.end_pos)

    @staticmethod
    def create_cnn_line(block, connector_id, pos) -> None:
        match connector_id:
            case 1:
                x = block.x + block.size[0] // 2
                y = block.y + block.size[1]
            case 2:
                x = block.x + block.size[0] // 2
                y = block.y
            case 3:
                x = block.x + block.size[0]
                y = block.y + block.size[1] // 2
            case _:
                x = block.x
                y = block.y + block.size[1] // 2

        block.cn_lines[connector_id] = ConnectLines((x, y), pos)

    @staticmethod
    def scope_check(pos) -> list:
        return [minmax(ConnectLines.available_zone[2], ConnectLines.available_zone[0], pos[0]),
                minmax(ConnectLines.available_zone[3], ConnectLines.available_zone[1], pos[1])]

    @staticmethod
    def delete_cnn_line(block, connector_id) -> None:
        block.cn_lines[connector_id] = 0

    @staticmethod
    def set_cnn_line_epos(block, connector_id, pos) -> None:
        block.cn_lines[connector_id].update_cords(0, *pos)

    @staticmethod
    def connect(block, line, pos):
        last_block, line_num = line
        line_index, conn_pos = block.get_side(*pos)

        last_block.cn_lines[line_num].end_pos = conn_pos

        block.cn_lines[line_index] = last_block.cn_lines[line_num]

    @staticmethod
    def set_win(win):
        ConnectLines.win = win
