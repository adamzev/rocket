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
		return self.engine_count * self.throt * (self.thrust_sl + (pctVac * (self.thrust_vac - self.thrust_sl)))

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
		return self.thrustAtAlt(alt) / self.specificImpulseAtAlt(alt)

	def burnFuel(self, assignedThrust, alt, time_inc):
		self.fuelUsed += fuelBurnRate(assignedThrust, alt)
