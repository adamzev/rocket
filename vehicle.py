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
		self.ADC_error = [0.0]
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
		self.V_horiz_mph =[912.67]
		self.V_horiz_mph_inc = [0.0]
		self.V_total = [0.0]
		self.total_eff = [0.0]
		self.ADC_predicted = [0.0]
		self.ADC_actual = [0.0]
		self.orbitalV = orbitalVelocity(current(self.alt))

	def set_alt(self, alt):
		self.alt.append(alt)


	def get_alt(self, when = "current"):
		return get_value(self.alt, when)

	def get_V_horiz_mph(self, when = "current"):
		return get_value(self.V_horiz_mph, when)

	def get_V_vert_inc(self, when = "current"):
		return get_value(self.V_vert_inc, when)

	def get_V_horiz_mph_inc(self, when = "current"):
		return get_value(self.V_horiz_mph_inc, when)

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

	def get_ADC_actual(self, when = "current"):
		return get_value(self.ADC_actual, when)

	def get_ADC_predicted(self, when = "current"):
		return get_value(self.ADC_predicted, when)

	def get_ADC_error(self, when = "current"):
		return get_value(self.ADC_error, when)

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

	def update_V(self, time_inc):
		self.updateIncVertV(time_inc)
		self.update_V_vert()
		self.update_V_horiz_mph_inc(time_inc)
		self.update_V_horiz_mph()


	def updateIncVertV(self, time_inc):
		avg_A_vert_eff = average(self.get_A_vert_eff(), self.get_A_vert_eff("prev"))
		self.V_vert_inc.append(avg_A_vert_eff * time_inc * ACCEL_OF_GRAVITY)

	def update_V_vert(self):
		self.V_vert.append(self.get_V_vert() + self.get_V_vert_inc())

	def update_V_horiz_mph_inc(self, time_inc):
		avg_A_horiz = average(self.get_A_horiz(), self.get_A_horiz("prev"))
		self.V_horiz_mph_inc.append(avg_A_horiz * time_inc * ACCEL_OF_GRAVITY)


	def update_V_horiz_mph(self):
		self.V_horiz_mph.append(self.get_V_horiz_mph() + fpsToMph(self.get_V_horiz_mph_inc()))




	def updateA(self, predictedADC):
		self.ADC_actual.append(ADC(self.get_airSpeed(), self.get_alt(), self.adc_K))  # with resultant ADC in  "g" units
		self.ADC_predicted.append(predictedADC)

		self.ADC_error.append(self.get_ADC_predicted("prev") - self.get_ADC_actual())
		totalA = self.totalThrust / self.currentWeight

		self.A_total.append(totalA)
		self.A_total_eff.append(totalA - predictedADC + self.get_ADC_error())
		#self.ADC_prediction_report(predictedADC, self.get_ADC_error())

	def ADC_prediction_report(self, predictedADC, error):
		print ("Actual ADC={} predictedADC={} error={}".format(self.get_ADC_actual(), predictedADC, error))

	def updateVertA(self, assignedA_vert, calcG = True):
		orbitalV = orbitalVelocity(current(self.alt))
		G = bigG(self.get_V_horiz_mph(), orbitalV)
		self.orbitalV = orbitalVelocity(current(self.alt))


		if calcG:
			self.A_vert.append(assignedA_vert)
			self.A_vert_eff.append(assignedA_vert - G)
		else:
			self.A_vert.append(assignedA_vert + G)
			self.A_vert_eff.append(assignedA_vert)

	def updateHorizA(self):
		try:
			self.A_horiz.append(math.sqrt(self.get_A_total_eff()**2 - self.get_A_vert()**2))

		except:
			raise ValueError("Sqrt of negative, A total={} which is > A_vert={}".format(self.get_A_total_eff("prev"), self.get_A_vert()))



	def get_airSpeed(self):
		return pythag(fpsToMph(self.get_V_vert()), self.get_V_horiz_mph()-912.67)

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

	def setEngineAssignedThrustPerEngine(self, engineName, thrust):
		engine = self.findEngine(engineName)
		if thrust == "max":
			engine.set_assigned_thrust_per_engine(engine.thrust_sl)
		else:
			engine.set_assigned_thrust_per_engine(thrust)


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

	def handle_event(self, event, time, time_inc):

		'''
		SAMPLE EVENTS
		events = [
				{
					"name" : "Reduce Thrust",
					"engine": "SRM",
					"start_time": 24.00,
					"end_time" : 45.00,
					"rate" : -20000.0,
				},
				{
					"name" : "Reduce Thrust Until Depleted",
					"engine": "SRM",
					"start_time": 99.00,
					"end_time" : 114.00,
				},
				{
					"name" : "Jettison",
					"engine": "SRM",
					"start_time": 114.00,
					"end_time" : 114.00,
				},
				{
					"name" : "Reduce Throttle",
					"engine": "RD-171M",
					"start_time": 137.00,
					"end_time" : 140.00,
				},
			]
		'''
		if event["name"] == "Reduce Thrust" and time < event["end_time"]:
			engine = self.findEngine(event["engine"])
			currentThrust = engine.get_thrust_per_engine()
			newThrust = currentThrust + event["rate"] * time_inc
			engine.set_assigned_thrust_per_engine(newThrust)
			print("\nEVENT: Reduced thrust of {} to {}".format(engine.name, newThrust))
