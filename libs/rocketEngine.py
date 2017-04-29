import logging
from generalEquations import *
from util import *
from util.text_interface import *

class RocketEngine:
	def __init__(self, engineStats):
		self.throt = [0.0]
		self.burn_rate = []
		self.messages = []
		self.thrust_total = [0.0]
		for key, value in engineStats.iteritems():
			setattr(self, key, value)

	def __str__(self):
		return "Name={} Throt={} Eff Burn Rate={} Thrust={}".format(self.name, self.throt_avg, self.get_eff_fuel_burn_rate(), self.get_thrust_total())

	@staticmethod
	def factory(engine_data):
		''' creates engines that burn either solid or liquid fuel '''
		if engine_data["type"] == "Solid":
			return SolidRocketEngine(engine_data)
		elif engine_data["type"] == "Liquid":
			return LiquidRocketEngine(engine_data)
		else:
			raise ValueError("Unsupported engine type.")

	def set_fuel_source(self, source):
		self.fuel_source = source

	def setThrottleOverride(self, requested_throt):
		# allows setting throttle without powering up the engine
		self.throt.append(requested_throt)

	@property
	def throt_avg(self):
		return average(self.get_throt(), self.get_throt("prev"))

	def get_throt(self, when = "current"):
		return get_value(self.throt, when)

	def get_burn_rate(self, when = "current"):
		return get_value(self.burn_rate, when)


	def get_thrust_total(self, when = "current"):
		return get_value(self.thrust_total, when)

	def get_thrust_per_engine(self, when = "current"):
		return get_value(self.thrust_total, when) / self.engine_count

	def setThrottle(self, requested_throt, time_inc = 1):
		#Limit the throttle to its max change limit
		if requested_throt > self.get_throt():
			direction = 1.0
			verb = "increased"
		else:
			direction = -1.0
			verb = "decreased"
		#direction 1 for pos and -1 for neg changes
		if abs(requested_throt - self.get_throt()) > (self.throt_rate_of_change_limit * time_inc):
			throt = self.get_throt() + time_inc * self.throt_rate_of_change_limit * direction
		else:
			throt = requested_throt
		if throt > self.max_throt:
			logging.debug("Max Throt achieved for {}".format(self.name))
			self.throt.append(self.max_throt)
		elif throt < self.min_throt:
			if direction < 0:
				logging.debug("{} Engine shutoff".format(self.name))
				self.throt.append(0)
			else:
				logging.debug("{} Engine set to min throt".format(self.name))
				self.throt.append(self.min_throt)
		else:
			self.throt.append(throt)
		endThrottle = self.get_throt()
		self.messages.append("\nEVENT: {} Throttle {} from {} to {} time inc {}".format(self.name, verb, self.get_throt("prev"), self.get_throt(), time_inc))

	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1.0 - patm

		self.thrust_total.append(self.engine_count * self.get_throt() * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl))))
		return self.get_thrust_total()

	def reduceThrottlePerc(self, perc):
		self.throt.append(self.throt - perc)

	def get_eff_fuel_burn_rate(self, for_all = True):
		if for_all:
			return self.throt_avg * self.get_burn_rate() * self.engine_count
		else:
			return self.throt_avg * self.get_burn_rate()

	def burn_fuel(self, time_inc, alt = None):
		# alt is ignored for this engine type
		if self.throt_avg > 0.0:
			print self.name, "\nthrot_avg", self.throt_avg, "\neff burn rate", self.get_eff_fuel_burn_rate(),"\ntime_inc", time_inc, "\n\n"
			self.fuel_source.fuel_used += self.get_eff_fuel_burn_rate() * time_inc

	def specific_impulse_at_alt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		return self.specImp_sl + (pctVac * (self.specImp_vac - self.specImp_sl))


class SolidRocketEngine(RocketEngine):
	engine_type = "Solid"
	def __init__(self, engine_data):
		RocketEngine.__init__(self, engine_data)
		self.assigned_thrust = [0.0]
		self.assigned_burn_rates_for_SRM_power_down = [10064.81592, 8100, 5700, 4000, 2150, 0]
		#self.assigned_burn_rates_for_SRM_power_down = [10195.695, 8750, 5500, 3500, 2150]
		#self.assigned_thrust_per_engine_for_SRM_power_down = [3150000, 2729000, 2343000, 1473250, 937750, 576250, 0] other sim
		self.assigned_thrust_per_engine_for_SRM_power_down = [2625000, 2120000, 1498500, 1055000, 568570, 0]
	def set_assigned_thrust_per_engine(self, thrust):
		self.thrust_total.append(thrust * self.engine_count)
	def burn_fuel(self, time_inc, alt):

		if self.throt_avg > 0.0:
			self.burn_rate.append(self.get_thrust_total()  / self.specific_impulse_at_alt(alt))
			self.fuel_source.fuel_used += self.get_burn_rate() * time_inc * self.get_throt()
		# print "solid rocket {} at alt {}".format(self.get_burn_rate(), alt)
	def adjust_thrust_to_burn_at_rate_per_engine(self, rate, alt):
		self.burn_rate.append(rate)
		self.burn_rate.append(rate)
		thrust = rate * self.specific_impulse_at_alt(alt)
		throt = thrust / self.thrust_sl

		self.set_assigned_thrust_per_engine(thrust)
		self.set_assigned_thrust_per_engine(thrust)

	def reduceThrust(self, rate, time_inc):
		currentThrust = self.get_thrust_per_engine()
		newThrust = currentThrust + rate * time_inc
		self.set_assigned_thrust_per_engine(newThrust)
		print("\nEVENT: Reduced thrust of {} to {}".format(self.name, newThrust))

	def power_down(self, start_time, end_time, time, time_inc, alt):
		eventTime = end_time - start_time
		fuelRemaining = self.fuel_source.get_fuel_remaining()
		srm_entry_mode = "array"
		print ("\nEVENT: power down {}".format(self.name))
		if srm_entry_mode == "manual":
			thrust = raw_input("Enter the assigned SRM thrust per engine:")
		if srm_entry_mode == "array" and len(self.assigned_burn_rates_for_SRM_power_down)>0:
			burn_rate = self.assigned_burn_rates_for_SRM_power_down.pop(0)
			self.adjust_thrust_to_burn_at_rate_per_engine(burn_rate, alt)
		if srm_entry_mode == "array_thrust" and len(self.assigned_thrust_per_engine_for_SRM_power_down)>0:
			self.set_assigned_thrust_per_engine(self.assigned_thrust_per_engine_for_SRM_power_down.pop(0))
		if srm_entry_mode == "linear":
			pass
		if srm_entry_mode == "cube root":
			pass
	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1.0 - patm
		return self.get_thrust_total() * self.get_throt()



class LiquidRocketEngine(RocketEngine):
	engine_type = "Liquid"
