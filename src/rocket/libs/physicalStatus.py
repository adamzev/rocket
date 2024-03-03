import sys
sys.path.append('/home/tutordelphia/www/rocket/')

from util import *
from libs.acceleration import Acceleration
from libs.velocity import Velocity
import generalEquations as equ

class PhysicalStatus(object):
	def __init__(self, A_horiz = 0.0, A_vert = 0.0, V_horiz = 0.0, V_vert = 0.0, alt = 0.0, force = 0.0, earth_rotation_mph = 912.67):
		self._A = Acceleration(A_horiz, A_vert)
		self._V = Velocity(V_horiz, V_vert, earth_rotation_mph)
		self._alt = alt
		self._ADC_predicted = 0.0
		self._ADC_actual = 0.0
		self._ADC_error = 0.0
		self._weight = 0.0
		self.force = force


	def __str__(self):
		return "{} {} alt={}".format(self.A, self.V, self.alt)

	@property
	def weight(self):
		return self._weight

	@weight.setter
	def weight(self, value):
		self._weight = value

	@property
	def A(self):
		return self._A

	@property
	def V(self):
		return self._V

	@property
	def ADC_predicted(self):
		return self._ADC_predicted

	@ADC_predicted.setter
	def ADC_predicted(self, value):
		self._ADC_predicted = value


	@property
	def ADC_actual(self):
		return self._ADC_actual

	@ADC_actual.setter
	def ADC_actual(self, value):
		self._ADC_actual = value

	@property
	def ADC_error(self):
		return self._ADC_error

	@ADC_error.setter
	def ADC_error(self, value):
		self._ADC_error = value

	@property
	def alt(self):
		return self._alt

	@alt.setter
	def alt(self, value):
		self._alt = value

	@property
	def big_G(self):
		return self._big_G

	def set_big_G(self):
		self._big_G = equ.bigG(self.V.horiz_mph, self.V.get_orbital(self.alt))

	@property
	def A_vert_eff(self):
		return self.A.vert_eff

	@A_vert_eff.setter
	def A_vert_eff(self, value):
		self.A.vert_eff = value



	@alt.setter
	def alt(self, value):
		self._alt = value
