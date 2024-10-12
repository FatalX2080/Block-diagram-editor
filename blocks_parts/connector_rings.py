from zoneinfo import available_timezones

from pygame import draw

import styleSheet as Style


class ConnectorRings:
    win = None
    active_ring = None  # visible rings objects
    rings = set()  # all rings objects
    available_zone = None
    radius = None

    def __init__(self, block):
        self.cords = None
        self.visible = [0, 0, 0, 0]
        self.active = False

        self.block = block

        ConnectorRings.rings.add(self)

    def draw(self) -> None:
        if self.active :
            for vs, pos in zip(self.visible, self.cords):
                if vs:
                    draw.circle(ConnectorRings.win, Style.BLUE, pos, ConnectorRings.radius, 2)

    def hide(self) -> None:
        self.active = False
        self.visible = [0, 0, 0, 0]

    def set_cords(self, x, y, size, visible) -> None:
        offset = size[1] // 5
        self.cords = ((x + size[0] // 2, y - offset),
                      (x + size[0] + offset, y + size[1] // 2),
                      (x + size[0] // 2, y + size[1] + offset),
                      (x - offset, y + size[1] // 2))
        if not visible:
            self.hide()
        self.scope_check()

    def switch_visible(self) -> bool:
        """
        Change visibility of connection rings on canvas
        """

        self.active = not self.active
        ConnectorRings.active_ring = None
        if self.active:
            self.scope_check()
            ConnectorRings.active_ring = self

        return self.active

    def scope_check(self) -> None:
        """
        Checking of available zone intersection
        """
        for i in range(4):
            x, y = self.cords[i]
            self.visible[i] = (ConnectorRings.available_zone[0] <= x <= ConnectorRings.available_zone[2] and
                               ConnectorRings.available_zone[1] <= y <= ConnectorRings.available_zone[3])

    def capture_check(self, x, y) -> tuple | None:
        """
        Check if mouse click by this block
        :param x: mouse x click
        :param y: mouse y click
        :return: (block ref; ring num)
        """
        for i in range(4):
            rx, ry = self.cords[i]
            if abs(x - rx) <= ConnectorRings.radius * 1.5 and abs(y - ry) <= ConnectorRings.radius * 1.5:
                return self.block, i
        return None, None

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def connect_ring_capture(pos) -> tuple:
        """
        Check all blocks for capturing
        :param pos: (click.x, click.y)
        :return: (**block ref**; **ring num**) if find None else
        """
        x, y = pos
        if ConnectorRings.active_ring is not None:
            return ConnectorRings.active_ring.capture_check(x, y)
        return None, None

    @staticmethod
    def set_win(win) -> None:
        ConnectorRings.win = win

    @staticmethod
    def set_available_zone(available) -> None:
        ConnectorRings.available_zone = available
