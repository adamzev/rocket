import logging
from generalEquations import *
class RocketEngine:
	def __init__(self, engineStats):
		self.throt = [0.0]
		self.fuelUsed = 0.0
		for key, value in engineStats.iteritems():
			setattr(self, key, value)

	def setThrottle(self, perc):
		self.throt.append(perc)

	def thrustAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		n = len(self.throt)-1
		self.thrust = self.engine_count * self.throt[n] * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl)))
		return self.thrust

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
	def burnFuel(self, time_inc):
		n = len(self.throt)-1
		throt_avg = average(self.throt[n], self.throt[n-1])
		self.fuelUsed += throt_avg * self.burn_rate * self.engine_count



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


'''	def specificImpulseAtAlt(self, alt):
		patm = percentOfAtmosphericPressure(alt)
		pctVac = 1 - patm
		return self.specImp_sl + (pctVac * (self.specImp_vac - self.specImp_sl))
'''
