import logging
from util import func

import generalEquations as equ
import mode

class RocketEngine(object):
	def __init__(self, engineStats):
		self.attached = True
		self.throt_cur = 0.0
		self.throt_prev = 0.0
		self.burn_rate = 0.0
		self.messages = []
		self.thrust_total = 0.0
		self.reached_max = False

		# The following are overwritten by engine stats
		self.event = {}
		self.power_down_start_time = None
		self.ignition_time = None
		self.jettison_time = None
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

		if self.power_down_start_time:
			self.power_down_start_time = round(self.power_down_start_time, 1)
		if self.ignition_time:
			self.ignition_time = round(self.ignition_time, 1)
		if self.jettison_time:
			self.jettison_time = round(self.jettison_time, 1)
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


	def engine_stats(self, starting_throttle, power_down_start_time, ignition_time=None, jettison_time=None):

		stat_time = 0.0
		if ignition_time:
			stat_time = ignition_time

		if power_down_start_time == float('inf'):
			sim_end = stat_time + 6
			# 6 seconds is more than enough time for any engine to hit max
		else:
			sim_end = power_down_start_time + 5.0
		time_inc = 0.1
		stats = {
			"max_reached_time": None,
			"engine_cutoff_time": None,
			"min_reached_time" : None,
			"throttle_at_end_time": None
		}
		if starting_throttle == 0 and not ignition_time:
			# if the engine is never turned on, get out of here
			return stats
		max_reached = False
		min_reached = False
		self.setThrottleOverride(starting_throttle)
		self.setThrottleOverride(starting_throttle)
		while stat_time < sim_end:
			#print(stat_time, self.throt_cur)
			if stat_time != 0:
				self.events(stat_time, time_inc)
			if not max_reached:
				if self.throt_cur == self.max_throt:
					max_reached = True
					stats['max_reached_time'] = stat_time

			if stat_time == jettison_time:
				stats['engine_cutoff_time'] = stat_time

				return stats
			if max_reached and not min_reached and func.less_than_or_almost_equals(self.throt_avg, self.min_throt):
				min_reached = True
				stats['min_reached_time'] = stat_time

			if max_reached and self.throt_avg == 0.0:
				stats['engine_cutoff_time'] = stat_time
				return stats
			stats['throttle_at_end_time'] = self.throt_cur # keep updating the throttle at end, until the end
			stat_time += time_inc
		return stats



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
		self.throt_prev = self.throt_cur
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

	def events(self, time, time_inc):
		decimal_precision = 3
		if self.throt_avg > 0.0 and not self.reached_max:
			self.setThrottle(self.max_throt, time_inc)
			if self.throt_avg == self.max_throt:
				self.reached_max = True




class SolidRocketEngine(RocketEngine):
	engine_type = "Solid"
	def __init__(self, engine_data):
		RocketEngine.__init__(self, engine_data)
		self.power_down_start_time = None
		self.power_down_fuel_level = engine_data["power_down_fuel_level"]
		self.power_down_burn_rates = engine_data["power_down_burn_rates"]

	def set_assigned_thrust_per_engine(self, thrust):
		self.thrust_total = thrust * self.engine_count

	def burn_fuel(self, time_inc, alt):

		if self.throt_avg > 0.0:
			self.burn_rate = self.get_thrust_total()  / self.specific_impulse_at_alt(alt)
			self.fuel_source.fuel_used += self.get_burn_rate() * time_inc * self.get_throt()
		# print "solid rocket {} at alt {}".format(self.get_burn_rate(), alt)
	def adjust_thrust_to_burn_at_rate_per_engine(self, rate, alt):
		thrust = rate * self.specific_impulse_at_alt(alt)
		message = "EVENT: Set burn rate of {} (thrust = {})".format(rate, thrust)
		self.messages.append(message)
		self.set_assigned_thrust_per_engine(thrust)

	def change_thrust(self, rate, time_inc):
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

	def thrustAtAlt(self, alt):
		return self.get_thrust_total() * self.get_throt()


	def events(self, time, time_inc):
		super(SolidRocketEngine, self).events(time, time_inc)
		if self.event:
			if func.between_floats(time, self.event["start_time"], self.event["end_time"]):
				if self.event["name"] == "Change Thrust" and time < self.event["end_time"]:
					self.change_thrust(self.event["rate"], time_inc)

	def power_down_by_burn_rates(self, time, alt, stage):
		time_since_start = time - self.power_down_start_time
		if func.almost_equal(time_since_start, round(time_since_start)):
			try:
				self.burn_rate_per_engine = self.power_down_burn_rates.pop(0)
			except IndexError:
				stage.jettison()
		if stage.attached:
			self.adjust_thrust_to_burn_at_rate_per_engine(self.burn_rate_per_engine, alt)

class LiquidRocketEngine(RocketEngine):
	''' Liquid Rocket Engine class '''
	power_down_in_progress = False
	engine_type = "Liquid"
	def events(self, time, time_inc):
		super(LiquidRocketEngine, self).events(time, time_inc)
		if self.ignition_time and func.almost_equal(time, self.ignition_time, 0.1):
			self.setThrottle(self.min_throt, time_inc)

		if self.power_down_in_progress or self.power_down_start_time and func.almost_equal(time, self.power_down_start_time, 0.1):
			self.setThrottle(0, time_inc)
			self.power_down_in_progress = True
			if self.throt_avg == 0:
				self.power_down_in_progress = False
