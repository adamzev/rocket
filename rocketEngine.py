import logging
from generalEquations import *
from util import *
class RocketEngine:
	def __init__(self, engineStats):
		self.throt = [0.0]
		self.burn_rate = []
		self.fuelUsed = 0.0
		self.thrust_total = [0.0]
		for key, value in engineStats.iteritems():
			setattr(self, key, value)
		self.usable_fuel = (1.0/ (1.0+self.residual)) * self.fuel

	def setThrottleOverride(self, requested_throt):
		# allows setting throttle without powering up the engine
		self.throt.append(requested_throt)

	def get_fuelUsed(self):
		return self.fuelUsed

	def get_throt(self, when = "current"):
		return get_value(self.throt, when)

	def get_burn_rate(self, when = "current"):
		return get_value(self.burn_rate, when)


	def get_thrust_total(self, when = "current"):
		return get_value(self.thrust_total, when)

	def get_thrust_per_engine(self, when = "current"):
		return get_value(self.thrust_total, when) / self.engine_count


	def set_assigned_thrust_per_engine(self, thrust):
		self.thrust_total.append(thrust * self.engine_count)

	def setThrottle(self, requested_throt, time_inc = 1):
		#Limit the throttle to its max change limit
		if abs(requested_throt - self.get_throt()) > (self.throt_rate_of_change_limit * time_inc):
			if requested_throt > self.get_throt():
				direction = 1.0
			else:
				direction = -1.0
			#direction 1 for pos and -1 for neg changes
			throt = self.get_throt() + time_inc * self.throt_rate_of_change_limit * direction
		else:
			throt = requested_throt
		if throt > self.max_throt:
			logging.debug("Max Throt achieved for {}".format(self.name))
			self.throt.append(self.max_throt)
		elif throt < self.min_throt:
			logging.debug("{} Engine shutoff".format(self.name))
			self.throt.append(0)
		else:
			self.throt.append(throt)

	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		try: #if thrust controlled
			thrust_controlled = self.thrust_controlled
			return self.get_thrust_total() * self.get_throt()
		except:
			self.thrust_total.append(self.engine_count * self.get_throt() * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl))))
			return self.get_thrust_total()

	def reduceThrottlePerc(self, perc):
		self.throt.append(self.throt - perc)

	def adjust_throttle_to_burn_at_rate_per_engine(self, rate, alt):
		assert self.name == "SRM"
		thrust = rate * self.specific_impulse_at_alt(alt)

		throt = thrust / self.thrust_sl

		print("Rate ={} \nThrust={} \n Throt={}".format(rate, thrust,throt))
		self.setThrottleOverride(throt)

	def burnFuel(self, time_inc, alt = None):
		throt_avg = average(self.get_throt(), self.get_throt("prev"))

		if throt_avg == 0:
			return self.fuelUsed
		else:
			try:
				thrust_controlled = self.thrust_controlled
				self.burn_rate.append(self.get_thrust_total()  / self.specific_impulse_at_alt(alt))
				self.fuelUsed += self.get_burn_rate() * time_inc

			except:
				self.fuelUsed += throt_avg * self.get_burn_rate() * self.engine_count * time_inc

	def getUsableFuelRemaining(self):
		return self.usable_fuel-self.fuelUsed
	def getFuelRemaining(self):
		return self.fuel-self.fuelUsed

	def specific_impulse_at_alt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		return self.specImp_sl + (pctVac * (self.specImp_vac - self.specImp_sl))
