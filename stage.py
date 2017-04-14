from rocketEngine import *
from generalEquations import *
from util import *


class Stage:

	def __init__(self, stage_specs):
		self.fuel_used = 0.0
		for key, value in stage_specs.iteritems():
			setattr(self, key, value)

		def get_fuel_used(self):
			return stage.fuel_used

		def get_fuel_remaining(self):
			return self.fuel - self.fuelUsed
