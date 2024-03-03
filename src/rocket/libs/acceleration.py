from libs.twoD import TwoD


class Acceleration(TwoD):
    def __init__(self, horiz, vert):
        TwoD.__init__(self, horiz, vert)
        self._vert_eff = 0.0

    def __str__(self):
        return "A h = {}  A v = {} A total = {}".format(
            self.horiz, self.vert, self.total
        )

    def eff(self):
        pass
        # self._eff = eff

    @property
    def vert_eff(self):
        return self._vert_eff

    @vert_eff.setter
    def vert_eff(self, value):
        self._vert_eff = value

    def set_raw(self, force, mass):
        self.raw = force / mass
