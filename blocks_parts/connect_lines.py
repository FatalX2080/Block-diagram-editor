import styleSheet as Style
from pygame import draw


class ConnectLines:
    win = None

    def __init__(self, io, spos, epos):
        self.io = io
        self.start_pos = list(spos)
        self.end_pos = list(epos)

    def draw(self) -> None:
        draw.line(ConnectLines.win, Style.BLACK, self.start_pos, self.end_pos)

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
    def set_win(win):
        ConnectLines.win = win
