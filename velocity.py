from generalEquations import *
from util import *
class Velocity(TwoD):
	def __init__(self, horiz, vert, v_vert_inc = None):
		TwoD.__init__(horiz, vert)
		self._V_vert_inc = v_vert_inc
		self.earth_rotation_mph = 912.67


	@property
	def eff(self):
		pass
		#self._eff = eff

	@property
	def vert_eff(self):
		pass
		#self._eff = eff

	@property
	def horiz_mph(self):
		pass
		#self._eff = eff

	@property
	def vert_mph(self):
		return fpsToMph(self.vert)
		#self._eff = eff


	@property
	def air_speed(self):
		return pythag(vert_mph, self.horiz_mph-self.earth_rotation_mph)
		
	@vert.setter
	def vert(self, value):
		self._vert = value
		self.update()


	def V_horiz_mph_inc(self):
		pass
		#self._eff = eff
