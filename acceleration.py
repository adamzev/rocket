from generalEquations import *
from twoD import TwoD

from util import *
class Acceleration(TwoD):
	def __init__(self, horiz, vert):
		TwoD.__init__(self, horiz, vert)

	def __str__(self):
		return "A h = {}  A v = {} A total = {}".format(self.horiz, self.vert, self.total)

	@property
	def eff(self):
		pass
		#self._eff = eff


	def set_raw(self, force, mass):
		self.raw = force / mass
