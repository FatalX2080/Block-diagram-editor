import styleSheet as Style
from pygame import draw


class ConnectorRings:
    win = None
    active_ring = None  # visible rings objects
    rings = set()  # all rings objects
    available_zone = None

    def __init__(self, r, zone, block):
        self.radius = r
        self.cords = None

        self.block = block

        self.visible = [0, 0, 0, 0]
        self.active = False

        ConnectorRings.rings.add(self)
        ConnectorRings.available_zone = (zone[0] + self.radius, zone[1] + self.radius,
                                         zone[2] - self.radius, zone[3] - self.radius)

    def draw(self) -> None:
        if self.active:
            for vs, pos in zip(self.visible, self.cords):
                if not vs:
                    continue
                draw.circle(ConnectorRings.win, Style.BLUE, pos, self.radius, 2)

    def hide(self) -> None:
        self.active = False
        self.visible = [0, 0, 0, 0]

    def set_cords(self, cords, visible) -> None:
        self.cords = cords
        if not visible:
            self.hide()
        self.scope_check()

    def switch_visible_rings(self) -> bool:
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
        :return:
        """
        for i in range(4):
            rx, ry = self.cords[i]
            if abs(x - rx) <= self.radius * 1.5 and abs(y - ry) <= self.radius * 1.5:
                return self.block, i + 1
        return None

    # ------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_win(win):
        ConnectorRings.win = win
