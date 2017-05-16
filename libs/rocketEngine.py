import logging
from util import func
from util.text_interface import *
import generalEquations as equ
import mode

class RocketEngine:
	def __init__(self, engineStats):
		self.attached = True
		self.throt_cur = 0.0
		self.throt_prev = 0.0
		self.burn_rate = 0.0
		self.messages = []
		self.thrust_total = 0.0

		# The following are overwritten by engine stats
		self.min_throt = 0.0
		self.max_throt = 1.0
		self.engine_count = 0
		self.thrust_sl = 0.0
		self.thrust_vac = 0.0
		self.stage = None
		self.throt_rate_of_change_limit = 1.0
		self.name = "Not set yet"
		self.specImp_sl = 0.0
		self.specImp_vac = 0.0

		for key, value in engineStats.iteritems():
			setattr(self, key, value)

	def __str__(self):
		return "Name={} Throt={} Eff Burn Rate={} Thrust={} Count={} Stage={}".format(self.name, self.throt_avg, self.get_eff_fuel_burn_rate(), self.get_thrust_total(), self.engine_count, self.stage)


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

	def requested_throt_to_float(self, requested_throt):
		''' Converts the requested throttle to a floating point number between 0.0 and 1.0 '''
		assert func.is_float(requested_throt) or requested_throt in ["min", "max", "off"]
		if requested_throt == "max":
			requested_throt = self.max_throt
		elif requested_throt == "min":
			requested_throt = self.min_throt
		elif requested_throt == "off":
			requested_throt = 0.0

		if requested_throt >= self.max_throt:
			requested_throt = self.max_throt
		assert func.is_float(requested_throt) and requested_throt >= 0.0 and requested_throt <= 1.0
		return requested_throt

	def setThrottleOverride(self, requested_throt):
		''' allows setting throttle without regard to the engine's max rate of change '''

		requested_throt = self.requested_throt_to_float(requested_throt)
		self.throt_cur = requested_throt

	@property
	def throt_avg(self):
		return equ.average(self.get_throt(), self.get_throt("prev"))

	def get_throt(self, when="current"):
		if when == "current":
			return self.throt_cur
		elif when == "prev":
			return self.throt_prev
		else:
			raise ValueError("Only current and prev values stored")

	def get_burn_rate(self, when="current"):
		return self.burn_rate


	def get_thrust_total(self, when="current"):
		return self.thrust_total

	def get_thrust_per_engine(self):
		return self.thrust_total / self.engine_count

	def setThrottle(self, requested_throt, time_inc):
		self.throt_prev = self.throt_cur
		#Limit the throttle to its max change limit
		requested_throt = self.requested_throt_to_float(requested_throt)

		if requested_throt == self.get_throt():
			self.throt_cur = requested_throt
			return requested_throt

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
			logging.debug("Max Throt achieved for %s", self.name)
			self.throt_cur = self.max_throt
		elif throt < self.min_throt:
			if direction < 0:
				logging.debug("%s Engine shutoff", self.name)
				self.throt_cur = 0
			else:
				logging.debug("%s Engine set to min throt", self.name)
				self.throt_cur = self.min_throt
		else:
			self.throt_cur = throt

		if self.get_throt("prev") != self.get_throt():
			self.messages.append("\nEVENT: {} Throttle {} from {} to {} time inc {}".format(self.name, verb, self.get_throt("prev"), self.get_throt(), time_inc))

	def thrustAtAlt(self, alt):
		''' calculates the thrust at altitude and stores and returns that value '''
		patm = equ.percentOfAtmosphericPressure(alt)
		pctVac = 1.0 - patm
		if mode.THROTTLE_FINAL_UP and self.get_throt("prev") < self.get_throt():
			self.thrust_total = self.engine_count * self.get_throt() * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl)))
		else:
			self.thrust_total = self.engine_count * self.throt_avg * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl)))
		return self.get_thrust_total()

	def get_eff_fuel_burn_rate(self, for_all=True):
		''' returns the average throttle times the burn rate '''
		if for_all:
			return self.throt_avg * self.get_burn_rate() * self.engine_count
		else:
			return self.throt_avg * self.get_burn_rate()

	def burn_fuel(self, time_inc, alt=None):
		''' Burns fuel (increasing the total fuel used)
		Alt is ignored for this engine type
		'''
		if self.throt_avg > 0.0:
			inc_fuel_used = self.get_eff_fuel_burn_rate() * time_inc
			# print self.name, self.stage, "\nthrot_avg", self.throt_avg, "\neff burn rate", self.get_eff_fuel_burn_rate(), "\ntime_inc", time_inc, "\nInc fuel used", inc_fuel_used, "\n"
			self.fuel_source.fuel_used += inc_fuel_used

	def specific_impulse_at_alt(self, alt):
		''' calculates the specific impulse at the given altitude '''
		patm = equ.percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		return self.specImp_sl + (pctVac * (self.specImp_vac - self.specImp_sl))


class SolidRocketEngine(RocketEngine):
	engine_type = "Solid"
	def __init__(self, engine_data):
		RocketEngine.__init__(self, engine_data)
		self.assigned_thrust = 0.0
		self.assigned_burn_rates_for_SRM_power_down = [10064.81592, 8100, 5700, 4000, 2150, 0]
		#self.assigned_burn_rates_for_SRM_power_down = [10195.695, 8750, 5500, 3500, 2150]
		#self.assigned_thrust_per_engine_for_SRM_power_down = [3150000, 2729000, 2343000, 1473250, 937750, 576250, 0] other sim
		self.assigned_thrust_per_engine_for_SRM_power_down = [2625000, 2120000, 1498500, 1055000, 568570, 0]
	def set_assigned_thrust_per_engine(self, thrust):
		self.thrust_total = thrust * self.engine_count

	def burn_fuel(self, time_inc, alt):

		if self.throt_avg > 0.0:
			self.burn_rate = self.get_thrust_total()  / self.specific_impulse_at_alt(alt)
			self.fuel_source.fuel_used += self.get_burn_rate() * time_inc * self.get_throt()
		# print "solid rocket {} at alt {}".format(self.get_burn_rate(), alt)
	def adjust_thrust_to_burn_at_rate_per_engine(self, rate, alt):
		self.burn_rate = rate
		thrust = rate * self.specific_impulse_at_alt(alt)
		throt = thrust / self.thrust_sl

		self.set_assigned_thrust_per_engine(thrust)
		self.set_assigned_thrust_per_engine(thrust)

	def changeThrust(self, rate, time_inc):
		currentThrust = self.get_thrust_per_engine()
		newThrust = currentThrust + rate * time_inc
		self.set_assigned_thrust_per_engine(newThrust)
		message = None
		if rate < 0:
			message = "\nEVENT: Reduced thrust of {} to {}".format(self.name, newThrust)
		if rate > 0:
			message = "\nEVENT: Increased thrust of {} to {}".format(self.name, newThrust)
		if message:
			self.messages.append(message)

	def power_down(self, start_time, end_time, time, time_inc, alt):
		eventTime = end_time - start_time #
		fuelRemaining = self.fuel_source.get_fuel_remaining()
		srm_entry_mode = "array"
		self.messages.append("\nEVENT: power down {}".format(self.name))
		if srm_entry_mode == "manual":
			thrust = raw_input("Enter the assigned SRM thrust per engine:")
			self.set_assigned_thrust_per_engine(thrust)
		if srm_entry_mode == "array" and self.assigned_burn_rates_for_SRM_power_down: # [] is False
			burn_rate = self.assigned_burn_rates_for_SRM_power_down.pop(0)
			self.adjust_thrust_to_burn_at_rate_per_engine(burn_rate, alt)
		if srm_entry_mode == "array_thrust" and self.assigned_thrust_per_engine_for_SRM_power_down:
			self.set_assigned_thrust_per_engine(self.assigned_thrust_per_engine_for_SRM_power_down.pop(0))
		if srm_entry_mode == "linear":
			pass
		if srm_entry_mode == "cube root":
			pass
	def thrustAtAlt(self, alt):
		return self.get_thrust_total() * self.get_throt()



class LiquidRocketEngine(RocketEngine):
	''' Liquid Rocket Engine class '''
	engine_type = "Liquid"
