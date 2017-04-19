from generalEquations import *
from util import *
from twoD import TwoD
import copy

class Velocity(TwoD):
	def __init__(self, horiz, vert, earth_rotation_mph = 912.67, vert_inc = 0.0, horiz_inc = 0.0):
		TwoD.__init__(self, horiz, vert)
		self._vert_inc = vert_inc
		self._horiz_inc = horiz_inc
		self.earth_rotation_mph = earth_rotation_mph


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

	@property
	def vert_inc(self):
		return self._vert_inc

	@vert_inc.setter
	def vert_inc(self, value):
		self._vert_inc = value

		
	@property
	def vert_mph(self):
		return fpsToMph(self.vert)


	def get_orbital(self, alt):
		return orbitalVelocity(alt)

	@property
	def air_speed(self):
		return pythag(self.vert_mph, self.horiz_mph-self.earth_rotation_mph)

	@property
	def horiz_mph_inc(self):
		return fpsToMph(self.horiz_inc)

	@horiz_mph_inc.setter
	def horiz_mph_inc(self, value):
		self._horiz_inc = mphToFps(value)
