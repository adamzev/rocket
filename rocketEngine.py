import logging
from generalEquations import *
from util import *
class RocketEngine:
	def __init__(self, engineStats):
		self.throt = [0.0]
		self.burn_rate = []
		self.fuelUsed = 0.0
		self.thrust = [0.0]
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


	def get_thrust(self, when = "current"):
		return get_value(self.thrust, when)

	def set_assigned_thrust(self, thrust):
		self.assigned_thrust = thrust * self.engine_count
		self.thrust.append(thrust)

	def setThrottle(self, requested_throt, time_inc = 1):
		#Limit the throttle to its max change limit
		if abs(requested_throt - current(self.throt)) > (self.throt_rate_of_change_limit * time_inc):
			# requested_throt/math.abs(requested_throt returns 1 for pos and -1 for neg changes
			throt = current(self.throt) + time_inc * self.throt_rate_of_change_limit * (requested_throt/abs(requested_throt))
		else:
			throt = requested_throt
		if throt > self.max_throt:
			logging.info("Max Throt achieved for {}".format(self.name))
			self.throt.append(self.max_throt)
		elif throt < self.min_throt:
			logging.info("{} Engine shutoff".format(self.name))
			self.throt.append(0)
		else:
			self.throt.append(throt)

	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		try: #if assigned_thrust exists
			self.thrust.append(self.assigned_thrust)
			return self.assigned_thrust
		except:
			self.thrust.append(self.engine_count * self.get_throt() * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl))))
			return self.get_thrust()

	def reduceThrottlePerc(self, perc):
		self.throt.append(self.throt - perc)

	'''
	def reduceThrottleToLBF(self, lbf, alt):
		currentLBF = self.thrustAtAlt(alt)
		self.throt = lbf / (currentLBF / self.throt)



	def reduceThrottleByLBF(self, lbf, alt):
		currentLBF = self.thrustAtAlt(alt)
		self.throt -= lbf / (currentLBF / self.throt)
	'''
	def burnFuel(self, time_inc, alt = None):
		throt_avg = average(current(self.throt), prev(self.throt))

		try:
			thrust_controlled = self.thrust_controlled
			self.burn_rate.append(self.get_thrust()  / self.specific_impulse_at_alt(alt))
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


'''
	def fuelBurnRate(self, alt):
		rate = self.thrustAtAlt(alt) / self.burn_rate
		logging.debug("Burn Rate of {}: {}".format(self.name, rate))
		return rate

	def burnFuel(self, alt, time_inc):
		fuelUsedInc = self.fuelBurnRate(alt) * time_inc
		self.fuelUsed += self.fuelBurnRate(alt) * time_inc
		logging.debug("Burn Used by {}: {}, {} total ".format(self.name, fuelUsedInc, self.fuelUsed))
'''
