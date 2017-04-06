from rocketEngine import *
from generalEquations import *

class Vehicle:

	def __init__(self, name, initialWeight, adc_K):
		self.name = name
		self.initialWeight = initialWeight
		self.currentWeight = initialWeight
		self.adc_K = adc_K
		self.engines = []
		self.alt = 30.0
		self.orbitalV = 0
		self.A_prev = self.A = {
			"vert_eff" : 0.0,
			"vert" : 0.0,
			"horiz" : 0.0,
			"total" : 0.0,
			"total_eff" : 0.0
		}
		self.V_prev = self.V = {
			"vert" : 0.0,
			"vert_inc" : 0.0,
			"horiz" : 912.67,
		}
		self.ADC_predicted = [0.0]
		self.ADC_actual = [0.0]
		self.orbitalV = orbitalVelocity(self.alt)

	def setAlt(self, alt):
		self.alt = alt

	def updateAlt (self, time_inc):
		self.alt = self.alt + (self.V_prev['vert'] * time_inc) + ((self.V_prev['vert_inc'] * time_inc) / 2.0 )

	def updatePrev(self):
		self.V_prev = self.V
		self.A_prev = self.A


	def attachEngine(self, engineData):
		engine = RocketEngine(engineData)
		self.engines.append(engine)

	def detachEngine(self, engineName):
		self.engines[:] = [d for d in self.engines if d.get('name') != engineName]

	def updateWeight(self, time_inc):
		fuelUsed = 0.0
		fuelBurn = 0.0
		for engine in self.engines:
			fuelUsed += engine.fuelUsed
		self.currentWeight = self.initialWeight - fuelUsed

	def updateIncVertV(self):
		self.V['vert'] = self.V_prev['vert'] + self.V_prev['vert_inc']

	def updateA(self, predictedADC):
		self.ADC_actual.append(((self.getAirSpeed() / 1000.0)**2) * percentOfAtmosphericPressure(self.alt) * self.adc_K)  # with resultant ADC in  "g" units
		self.ADC_predicted.append(predictedADC)
		error = prev(self.ADC_predicted) - current(self.ADC_actual)
		totalA = self.totalThrust / self.currentWeight
		self.A["total"] = totalA
		self.A["total_eff"] = totalA - predictedADC + error


	def updateVertA(self, assignedA_vert):
		A = self.A
		A_prev = self.A_prev

		orbitalV = orbitalVelocity(self.alt)
		self.orbitalV = orbitalVelocity(self.alt)
		A["vert"] = assignedA_vert
		avgVertV = average(A["vert"], A_prev["vert"])
		if avgVertV<= 0:
			avgVertV = A["total"]
		A["vert_eff"] = avgVertV - bigG(self.V["horiz"], orbitalV)
		self.A = A
	def updateHorizA(self):
		'''if self.A["total"]**2 >= self.A["vert"]**2:
			self.A["horiz"] = math.sqrt(self.A["total"]**2 - self.A["vert"]**2)
		else:
			self.A["horiz"] = 0
			logging.debug("ERROR: VertA is greater than total A: A: {} A vert: {} ".format(self.A["total"], self.A["vert"]))
			'''
		self.A["horiz"] = 0


	def updateVertV(self, time_inc):
		self.V["vert_inc"] = self.A["vert_eff"] * time_inc * ACCEL_OF_GRAVITY

	def getAirSpeed(self):
		return pythag(self.V["vert"], self.V["horiz"])

	def getTotalThrust(self):
		totalThrust = 0
		for engine in self.engines:
			totalThrust += engine.thrustAtAlt(self.alt)
		self.totalThrust = totalThrust
		return totalThrust

	def burnFuel(self, time_inc):
		for engine in self.engines:
			 engine.burnFuel(time_inc)

	def getTotalFuelUsed(self):
		fuelUsed = 0
		for engine in self.engines:
			fuelUsed += engine.fuelUsed
		return fuelUsed

	def setEngineThrottleOverride(self, engineName, throt):
		for engine in  self.engines:
			if engine.name == engineName:
				if throt == "max":
					engine.setThrottleOverride(engine.max_throt)
				else:
					engine.setThrottleOverride(throt)

	def setEngineThrottle(self, engineName, throt, time_inc):
		for engine in  self.engines:
			if engine.name == engineName:
				if throt == "max":
					engine.setThrottle(engine.max_throt, time_inc)
				else:
					engine.setThrottle(throt, time_inc)

	def getEngineThrottle(self, engineName):
		for engine in  self.engines:
			if engine.name == engineName:
				return engine.throt
