import libs
import util.func as func
import generalEquations as equ
import libs.query as q

class Stage:

	def __init__(self, stage_specs):
		self.fuel_used = 0.0
		self.fueling_engines = []
		self.holding_engines = []
		for key, value in stage_specs.iteritems():
			setattr(self, key, value)

	@staticmethod
	def select_engines(stage_name, fuel_type):
		
		add_more = True
		selected_engines = []
		while add_more:
			print "\n\nSelect engines for the {}".format(stage_name)
			this_engine = {}
			engine = libs.Vehicle.select_engine_from_list(stage_name, fuel_type)
			if engine:
				func.pretty_json(engine)
				engine_name = engine.keys()[0]
				# only accept integer values but store as float for compatibility
				count = float(q.query_int("How many {}s?".format(engine_name)))
				this_engine["engine_count"] = count
				this_engine["engine_name"] = engine_name
				this_engine["stage"] = engine[engine_name]["stage"]
				selected_engines.append(this_engine)
				print("{} {} engines are now attached.".format(int(count), this_engine["engine_name"]))
			else:
				add_more = False
		return selected_engines

	def fueling(self, engine):
		self.fueling_engines.append(engine)
	def __str__(self):
		return "Stage Name = {} Fuel Remaining = {} Burn Rate = {}".format(self.name, self.get_fuel_remaining(), self.get_fuel_burn_rate())

	def get_fuel_used(self):
		return self.fuel_used

	def get_fuel_remaining(self):
		fuel_remaining = self.fuel - self.fuel_used
		assert not self.attached or fuel_remaining > 0
		return fuel_remaining

	def get_fuel_burn_rate(self):
		burn = 0.0
		for engine in self.fueling_engines:
			burn += engine.get_eff_fuel_burn_rate()
		return burn

	def jettison(self):
		print("\nEVENT: Jettisoned {}".format(self.name))
		self.attached = False
		# if rocket total weight is calculated on total values change to be fueled_weight:
		# if rocket total weight is calculated on lift-off values use this:
		self.fuel_used = self.lift_off_weight
