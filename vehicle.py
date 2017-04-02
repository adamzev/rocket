from rocketEngine import *
from generalEquations import *

class Vehicle:
	alt = 0

	#VELOCITY
	vertV_prev = 0.0
	vertV_inc = 0.0
	vertV = 0.0

	horizV = 0.0

	#ACCELERATION
	vertA_eff = 0.0
	vertA_avg = 0.0
	vertA_prev = 0.0
	vertA = 0.0

	horizA_prev = 0.0
	horizA = 0.0

	def __init__(self, name, initialWeight, adc_K):
		self.name = name
		self.engines = []
		self.initialWeight = initialWeight
		self.currentWeight = initialWeight
		self.adc_K = adc_K

	def setAlt(self, alt):
		self.alt = alt

	def updateAlt (self, time_inc):
		self.alt = self.alt + (self.vertV_prev * time_inc) + ((self.vertV_inc * time_inc) / 2.0 )

	def updatePrev(self):
		self.horizA_prev = self.horizA
		self.vertA_prev = self.vertA
		self.vertV_prev = self.vertV


	def attachEngine(self, engineData):
		engine = RocketEngine(engineData)
		self.engines.append(engine)

	def updateWeight(self, time_inc):
		fuelUsed = 0.0
		fuelBurn = 0.0
		for engine in self.engines:
			fuelUsed += engine.fuelUsed
			fuelBurn += engine.fuelBurnRate(self.alt) * time_inc
		self.currentWeight = self.initialWeight - fuelUsed - fuelBurn

	def updateIncVertV(self):
		self.vertV = self.vertV_prev + self.vertV_inc

	def updateVertA(self):
		orbitalV = orbitalVelocity(self.alt)
		self.vertA = self.vertA_eff = self.vertA_avg - gravity(self.horizV, orbitalV) #does vertA equal vertA_eff?
		self.vertA_avg = (self.vertA + self.vertA_prev) / 2.0
	def updateVertV(self, time_inc):
		self.vertV_inc = self.vertA_eff * time_inc * ACCEL_OF_GRAVITY
	def updateHorizA(self):
		self.horizA_avg = (self.horizA + self.horizA_prev) / 2.0

	def getAirSpeed(self):
		return pythag(self.vertV, self.horizV)
