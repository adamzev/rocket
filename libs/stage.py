import util.func as func
import generalEquations as equ

class Stage:

	def __init__(self, stage_specs):
		self.fuel_used = 0.0
		self.fuel = 0.0
		self.lift_off_weight = 0.0
		self.name = "Not set"
		self.fueling_engines = []
		self.attached_engines = []
		self.attached = True
		for key, value in stage_specs.iteritems():
			setattr(self, key, value)

	def __str__(self):
		return "Stage Name = {} Fuel Remaining = {} Burn Rate = {}".format(self.name, self.get_fuel_remaining(), self.get_fuel_burn_rate())

	def attach_engine(self, engine):
		self.attached_engines.append(engine)

	def attached_engine_report(self):
		print (" \n {}".format(self.name))
		for engine in self.attached_engines:
			print(engine)

	def check_state(self):
		''' checks if the stage is in a valid state:
		If it is attached, is fuel remaining positive?
		'''
		fuel_remaining = self.fuel - self.fuel_used
		assert not self.attached or fuel_remaining > 0

	def fueling(self, engine):
		''' adds an engine to the list of engines that this stage is provide fuel for '''
		self.fueling_engines.append(engine)


	def get_fuel_used(self):
		return self.fuel_used

	def get_fuel_remaining(self):
		fuel_remaining = self.fuel - self.fuel_used
		self.check_state
		return fuel_remaining

	def get_fuel_burn_rate(self):
		burn = 0.0
		for engine in self.fueling_engines:
			burn += engine.get_eff_fuel_burn_rate()
		return burn

	def jettison(self):
		''' jettisons the stage and checks that attached engines are off '''
		print("\nEVENT: Jettisoned {}".format(self.name))
		self.attached = False
		for engine in self.attached_engines:
			if engine.type == "Liquid":
				assert engine.throt_cur <= engine.min_throt
			# set the average throttle of attached engines to zero
			engine.throt_cur = 0.0
			engine.throt_prev = 0.0
		# if rocket total weight is calculated on total values change to be fueled_weight:
		# if rocket total weight is calculated on lift-off values use this:
		self.fuel_used = self.lift_off_weight
