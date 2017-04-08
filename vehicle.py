from rocketEngine import *
from generalEquations import *
from util import *

class Vehicle:

	def __init__(self, name, initialWeight, adc_K):
		self.name = name
		self.initialWeight = initialWeight
		self.currentWeight = initialWeight
		self.adc_K = adc_K
		self.engines = []
		self.alt = [30.0]
		self.orbitalV = 0
		self.A_vert_eff = [0.0]
		self.A_vert = [0.0]
		self.A_horiz = [0.0]
		self.A_total = [0.0]
		self.A_total_eff = [0.0]
		self.V_vert = [0.0]
		self.V_vert_eff = [0.0]
		self.V_vert = [0.0]
		self.V_vert_inc = [0.0]
		self.V_horiz =[912.67]
		self.V_total = [0.0]
		self.total_eff = [0.0]
		self.ADC_predicted = [0.0]
		self.ADC_actual = [0.0]
		self.orbitalV = orbitalVelocity(current(self.alt))

	def set_alt(self, alt):
		self.alt.append(alt)


	def get_alt(self, when = "current"):
		return get_value(self.alt, when)

	def get_V_horiz(self, when = "current"):
		return get_value(self.V_horiz, when)

	def get_V_vert_inc(self, when = "current"):
		return get_value(self.V_vert_inc, when)

	def get_V_vert(self, when = "current"):
		return get_value(self.V_vert, when)

	def get_OrbitalV(self):
		return self.orbitalV

	def get_A_total(self, when = "current"):
		return get_value(self.A_total, when)

	def get_A_total_eff(self, when = "current"):
		return get_value(self.A_total_eff, when)

	def get_A_horiz(self, when = "current"):
		return get_value(self.A_horiz, when)

	def get_A_vert(self, when = "current"):
		return get_value(self.A_vert, when)


	def get_A_vert_eff(self, when = "current"):
		return get_value(self.A_vert_eff, when)

	def get_currentWeight(self):
		return self.currentWeight




	def updateAlt (self, time_inc):
		self.alt.append(altitude(self.get_alt(), self.get_V_vert("prev"), self.get_V_vert_inc(), time_inc))

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

	def updateVertV(self):
		self.V_vert.append(self.get_V_vert() + self.get_V_vert_inc())



	def updateA(self, predictedADC):
		self.ADC_actual.append(ADC(self.get_airSpeed(), self.get_alt(), self.adc_K))  # with resultant ADC in  "g" units
		self.ADC_predicted.append(predictedADC)
		error = prev(self.ADC_predicted) - current(self.ADC_actual)
		totalA = self.totalThrust / self.currentWeight
		self.A_total.append(totalA)
		self.A_total_eff.append(totalA - predictedADC + error)


	def updateVertA(self, assignedA_vert):
		orbitalV = orbitalVelocity(current(self.alt))
		self.orbitalV = orbitalVelocity(current(self.alt))
		self.A_vert.append(assignedA_vert)
		'''if(len(self.A_vert)>2):
			avgVertA = average(self.get_A_vert(), self.get_A_vert("prev"))
		else:
			avgVertA = self.get_A_vert()'''
		self.A_vert_eff.append(assignedA_vert - bigG(self.get_V_horiz(), orbitalV))

	def updateHorizA(self):
		'''if self.A["total"]**2 >= self.A["vert"]**2:
			self.A["horiz"] = math.sqrt(self.A["total"]**2 - self.A["vert"]**2)
		else:
			self.A["horiz"] = 0
			logging.debug("ERROR: VertA is greater than total A: A: {} A vert: {} ".format(self.A["total"], self.A["vert"]))
			'''
		self.A_horiz.append(0)

	def updateIncVertV(self, time_inc):
		avg_A_vert_eff = average(self.get_A_vert_eff(), self.get_A_vert_eff("prev"))
		self.V_vert_inc.append(avg_A_vert_eff * time_inc * ACCEL_OF_GRAVITY)

	def get_airSpeed(self):
		return fpsToMph(pythag(self.get_V_vert(), self.get_V_horiz()-912.67))

	def getTotalThrust(self):
		totalThrust = 0
		for engine in self.engines:
			totalThrust += engine.thrustAtAlt(self.get_alt())
		self.totalThrust = totalThrust
		return totalThrust

	def burnFuel(self, time_inc):
		for engine in self.engines:
			 engine.burnFuel(time_inc, self.get_alt())

	def getTotalFuelUsed(self):
		fuelUsed = 0
		for engine in self.engines:
			fuelUsed += engine.fuelUsed
		return fuelUsed

	def setEngineThrottleOverride(self, engineName, throt):
		engine = self.findEngine(engineName)
		if throt == "max":
			engine.setThrottleOverride(engine.max_throt)
		else:
			engine.setThrottleOverride(throt)

	def setEngineThrottle(self, engineName, throt, time_inc):
		engine = self.findEngine(engineName)
		if throt == "max":
			engine.setThrottle(engine.max_throt, time_inc)
		else:
			engine.setThrottle(throt, time_inc)

	def setEngineAssignedThrust(self, engineName, thrust):
		engine = self.findEngine(engineName)
		if thrust == "max":
			engine.set_assigned_thrust(engine.thrust_sl)
		else:
			engine.set_assigned_thrust(thrust)


	def getEngineThrottle(self, engineName):
		engine = self.findEngine(engineName)
		return engine.throt

	def findEngine(self, engineName):
		for engine in self.engines:
			if engine.name == engineName:
				return engine

	def engine_status(self, engineName = None):
		if engineName:
			engines = [self.findEngine(engineName)]
		else:
			engines = self.engines
		for engine in engines:
			print "Name: {}\nThrottle: {}\nThrust: {}\nFuel Used: {}".format(engine.name, engine.get_throt(),engine.get_thrust(), engine.get_fuelUsed())
