from generalEquations import *
from util import *
from acceleration import Acceleration

class PhysicalStatus:
	def __init__(self, A_horiz = None, A_vert = None, V_horiz = None, V_vert = None, alt = 0):
		self._A = Acceleration(A_horiz, A_vert)
		self._V = Velocity(V_horiz, V_vert)
		self._alt = alt
		self._orbitalV = orbitalVelocity(self.alt)
		self._ADC_predicted = 0
		self._ADC_actual = 0
		self._ADC_error = 0
		self._weight = 0


	def __str__(self):
		return "{} {} alt={} orbitalV={}".format(self.A, self.V, self.alt, self.orbitalV)

	@property
	def alt(self):
		return self._alt

	@alt.setter
	def alt(self, value):
		self._alt = value
		self.update_from_alt()

	@property
	def big_G(self):
		return bigG(self.V.horiz_mph, self.orbitalV)

	@alt.setter
	def alt(self, value):
		self._alt = value
		self.update_from_alt()


	def update_from_alt():
		self.orbitalV = orbitalVelocity(self.alt)
