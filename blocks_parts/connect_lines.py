from pygame import draw

import styleSheet as Style


def minmax(a, b, val) -> (int | float):
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

    def update_cords(self, side, dx=0, dy=0) -> None:
        match side:
            case 1:
                # end
                self.start_pos[0] -= dx
                self.start_pos[1] -= dy
            case -1:
                # start
                self.end_pos[0] -= dx
                self.end_pos[1] -= dy

        self.set_rendering_cords()

    def set_rendering_cords(self) -> None:
        self.rstart_pos = ConnectLines.scope_check(self.start_pos)
        self.rend_pos = ConnectLines.scope_check(self.end_pos)

    @staticmethod
    def scope_check(pos) -> list:
        return [minmax(ConnectLines.available_zone[2], ConnectLines.available_zone[0], pos[0]),
                minmax(ConnectLines.available_zone[3], ConnectLines.available_zone[1], pos[1])]


class Lines:
    def __init__(self):
        self.cn_lines = [0, 0, 0, 0]
        self.cn_lines_dir = [0, 0, 0, 0]  # 1 is out | -1 is input

    def draw(self) -> None:
        for line_iex in range(4):
            if self.cn_lines_dir[line_iex]:
                self.cn_lines[line_iex].draw()

    def update_cords(self, dx, dy) -> None:
        for line_iex in range(4):
            if self.cn_lines[line_iex]:
                self.cn_lines[line_iex].update_cords(self.cn_lines_dir[line_iex], dx, dy)

    def create_line(self, iex, start, end) -> None:
        self.cn_lines[iex] = ConnectLines(start, end)
        self.cn_lines_dir[iex] = 1

    def del_line(self, iex) -> None:
        self.cn_lines[iex] = 0
        self.cn_lines_dir[iex] = 0

    @staticmethod
    def create_cnn_line(block, connector_num, pos) -> None:
        match connector_num:
            case 0:
                x = block.x + block.size[0] // 2
                y = block.y + block.size[1]
            case 1:
                x = block.x + block.size[0]
                y = block.y + block.size[1] // 2
            case 2:
                x = block.x + block.size[0] // 2
                y = block.y + block.size[1]
            case _:
                x = block.x
                y = block.y + block.size[1] // 2

        block.lines.create_line(connector_num, (x, y), pos)

    @staticmethod
    def delete_cnn_line(block, connector_num) -> None:
        block.lines(connector_num)

    @staticmethod
    def set_cnn_line_epos(block, connector_num, pos) -> None:
        block.lines.cn_lines[connector_num].update_cords(-1, *pos)

    @staticmethod
    def connect(block, line, pos) -> None:
        last_block, line_num = line
        line_index, conn_pos = block.get_cn_side(*pos)
        last_block.lines.cn_lines[line_num].end_pos = conn_pos
        block.lines.cn_lines[line_index] = last_block.lines.cn_lines[line_num]
        block.lines.cn_lines_dir[line_index] = -1
        # TODO fix crutch
        block.lines.cn_lines[line_index].update_cords(-1)

    @staticmethod
    def set_win(win) -> None:
        ConnectLines.win = win

    @staticmethod
    def set_available_zone(zone) -> None:
        ConnectLines.available_zone = zone
