import styleSheet as Style
from pygame import draw


class ConnectLines:
    win = None

    def __init__(self, io, spos, epos, width=2):
        self.io = io
        self.start_pos = list(spos)
        self.end_pos = list(epos)
        self.width = width

    def draw(self) -> None:
        draw.line(ConnectLines.win, Style.BLACK, self.start_pos, self.end_pos, self.width)

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

        block.used_sides[connector_id] = ConnectLines(0, (x, y), pos)

    @staticmethod
    def delete_cnn_line(block, connector_id) -> None:
        block.used_sides[connector_id] = 0

    @staticmethod
    def set_cnn_line_epos(block, connector_id, pos) -> None:
        block.used_sides[connector_id].update_cords(0, *pos)


    @staticmethod
    def set_win(win):
        ConnectLines.win = win
