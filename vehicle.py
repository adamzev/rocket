from rocketEngine import *
from generalEquations import *

class Vehicle:
	alt = 0

	#VELOCITY
	V_prev = V = {
		"vert" : 0.0,
		"vert_inc" : 0.0,
		"horiz" : 0.0,
	}

	A_prev = A = {
		"vert_eff" : 0.0,
		"vert" : 0.0,
		"horiz" : 0.0
	}


	engines = []

	def __init__(self, name, initialWeight, adc_K):
		self.name = name
		self.initialWeight = initialWeight
		self.currentWeight = initialWeight
		self.adc_K = adc_K

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
			fuelBurn += engine.fuelBurnRate(self.alt) * time_inc
		self.currentWeight = self.initialWeight - fuelUsed - fuelBurn

	def updateIncVertV(self):
		self.V['vert'] = self.V_prev['vert'] + self.V_prev['vert_inc']

	def updateVertA(self):
		A = self.A
		A_prev = self.A_prev
		orbitalV = orbitalVelocity(self.alt)
		A["vert"] = A["vert_eff"] = average(A["vert"], A_prev["vert"]) - gravity(self.V["horiz"], orbitalV) #does vertA equal vertA_eff?
		self.A = A
	def updateVertV(self, time_inc):
		self.V["vert_inc"] = self.A["vert_eff"] * time_inc * ACCEL_OF_GRAVITY

	def getAirSpeed(self):
		return pythag(self.V["vert"], self.V["horiz"])
