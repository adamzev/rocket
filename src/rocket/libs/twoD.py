import generalEquations as equ


class TwoD(object):
    def __init__(self, horiz=0.0, vert=0.0, total=0.0):
        self._horiz = horiz
        self._vert = vert
        self._total = total

    @property
    def horiz(self):
        return self._horiz

    @horiz.setter
    def horiz(self, value):
        self._horiz = value

    @property
    def vert(self):
        return self._vert

    @vert.setter
    def vert(self, value):
        self._vert = value

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value

    def update(self, keep_horiz=True, keep_vert=True, keep_total=False):
        if keep_horiz and keep_vert:
            self._total = equ.pythag(self.horiz, self.vert, None)

        if keep_total and keep_vert:
            self._horiz = equ.pythag(None, self.vert, self.total)

        if keep_total and keep_horiz:
            self._vert = equ.pythag(self.horiz, None, self.total)
