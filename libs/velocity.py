from generalEquations import *
from util import *
from twoD import TwoD

class Velocity(TwoD):
	def __init__(self, horiz, vert, earth_rotation_mph = 912.67, vert_inc = 0.0, horiz_inc = 0.0):
		TwoD.__init__(self, horiz, vert)
		self._vert_inc = vert_inc
		self._horiz_inc = horiz_inc
		self.earth_rotation_mph = earth_rotation_mph

	@staticmethod
	def get_orbital(alt):
		''' Orbital Velocity (OV) is that horizontal velocity needed to counteract Earth's gravity at a given altitude
		OV decreases as you increase your radial distance from the center of the Earth, i.e. increase altitude.
		Alt in feet
		'''
		return orbitalVelocity(alt)

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
		return fpsToMph(self.horiz)

	@horiz_mph.setter
	def horiz_mph(self, value):
		self.horiz = mphToFps(value)

	@property
	def horiz_inc(self):
		return self._horiz_inc

	@horiz_inc.setter
	def horiz_inc(self, value):
		self._horiz_inc = value


	@property
	def vert_inc(self):
		return self._vert_inc

	@vert_inc.setter
	def vert_inc(self, value):
		self._vert_inc = value


	@property
	def vert_mph(self):
		return fpsToMph(self.vert)


	@property
	def air_speed_mph(self):
		return pythag(self.vert_mph, self.horiz_mph-self.earth_rotation_mph)

	@property
	def horiz_mph_inc(self):
		return fpsToMph(self.horiz_inc)

	@horiz_mph_inc.setter
	def horiz_mph_inc(self, value):
		self._horiz_inc = mphToFps(value)
