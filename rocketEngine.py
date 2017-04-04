import logging
from generalEquations import *
class RocketEngine:
	throt = 0.0
	fuelUsed = 0.0

	def __init__(self, engineStats):
		for key, value in engineStats.iteritems():
			setattr(self, key, value)

	def setThrottle(self, perc):
		self.throt = perc

	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		self.thrust = self.engine_count * self.throt * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl)))
		return self.thrust

	def specificImpulseAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		return self.specImp_sl + (pctVac * (self.specImp_vac - self.specImp_sl))

	def reduceThrottlePerc(self, perc):
		self.throt -= perc


	def reduceThrottleToLBF(self, lbf, alt):
		currentLBF = self.thrustAtAlt(alt)
		self.throt = lbf / (currentLBF / self.throt)



	def reduceThrottleByLBF(self, lbf, alt):
		currentLBF = self.thrustAtAlt(alt)
		self.throt -= lbf / (currentLBF / self.throt)

	def fuelBurnRate(self, alt):
		rate = self.thrustAtAlt(alt) / self.specificImpulseAtAlt(alt)
		logging.debug("Burn Rate of {}: {}".format(self.name, rate))
		return rate

	def burnFuel(self, alt, time_inc):
		fuelUsedInc = self.fuelBurnRate(alt) * time_inc
		self.fuelUsed += self.fuelBurnRate(alt) * time_inc
		logging.debug("Burn Used by {}: {}, {} total ".format(self.name, fuelUsedInc, self.fuelUsed))
