from rocketEngine import *
from generalEquations import *
from util import *


class Stage:

	def __init__(self, stage_specs):
		self.fuel_used = 0.0
		self.fueling_engines = []
		self.holding_engines = []
		for key, value in stage_specs.iteritems():
			setattr(self, key, value)

	def fueling(self, engine):
		self.fueling_engines.append(engine)
	def __str__(self):
		return "Stage Name = {} Fuel Remaining = {} Burn Rate = {}".format(self.type, self.get_fuel_remaining(), self.get_fuel_burn_rate())

	def get_fuel_used(self):
		return stage.fuel_used

	def get_fuel_remaining(self):
		return self.fuel - self.fuel_used

	def get_fuel_burn_rate(self):
		burn = 0.0
		for engine in self.fueling_engines:
			burn += engine.get_eff_fuel_burn_rate()
		return burn

	def jettison(self):
		print("\nEVENT: Jettisoned {}".format(self.type))
		# if rocket total weight is calculated on total values change to be fueled_weight:
		# if rocket total weight is calculated on lift-off values use this:
		self.fuel_used = self.initial_weight
