import math
import logging
import copy
import pprint

from generalEquations import *
from text_interface import *
from util import *
from title import *

log = logging.basicConfig(level=logging.INFO)
class Main_program:
	def __init__(self, specs = []):
		self.specs = specs
		self.alt = 30.0

		self.endTime = 10.0


	def start(self):
		print(TITLE)
		self.specs = get_specs()
		#self.events = get_events()
		self.events = [
			{
				"name" : "Increase Throttle By Max Rate-Of-Change",
				"engine": "RD-171M",
				"start_time": 0.00,
				"end_time" : 3.00,
			},
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
				"start_time": 114.10,
				"end_time" : 114.10,
			},
			{
				"name" : "Reduce Throttle By Max Rate-Of-Change",
				"engine": "RD-171M",
				"start_time": 137.00,
				"end_time" : 140.00,
			},
			{
				"name" : "Engine Cut-off",
				"engine": "RD-171M",
				"start_time": 140.00,
				"end_time" : 140.00,

			}
		]
		self.HLV = Vehicle(self.specs)


	def compute_row(self, rocket, events, predictedADC, assigned_V, printRow = True):
		rocket.set_ADC_predicted(predictedADC)
		for event in events:
			if rocket.time >= event["start_time"] and rocket.time <= event["end_time"]:
				rocket.handle_event(event, rocket.time, rocket.time_inc)

		#self.HLV.engine_status()

		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()
		#assigned_V = raw_input("Enter the assigned A_vert:")


		if assigned_V == "a" or assigned_V == "all":
			assigned_V = rocket.get_A_total_eff()
			rocket.updateVertA(assigned_V)
		else:
			assigned_V = float(assigned_V)
			rocket.updateVertA(assigned_V, False)



		rocket.updateHorizA()
		rocket.update_V(rocket.time_inc)
		rocket.updateAlt(rocket.time_inc)
		rocket.update_ADC_actual(rocket.time_inc)
		rocket.set_time_inc()
		rocket.tick()
		rocket.burnFuel(rocket.time_inc)

		if printRow:
			self.print_EdRow()

	def set_initial_conditions(self):
		if QUICKRUN:
			for i in range(2):
				self.HLV.setEngineThrottleOverride("RD-180", "max")
				self.HLV.setEngineThrottleOverride("SSME", "max")
				self.HLV.setEngineThrottleOverride("RD-171M", 0.56)
				self.HLV.setEngineThrottleOverride("SRM", 1)
				self.HLV.setEngineAssignedThrustPerEngine("SRM", "max")
		else:
			for engine in self.HLV.engines:
				answer = query_min_max("What is the starting throttle for {}".format(engine.name))
				# set each weight twice to set average weight
				self.HLV.setEngineThrottleOverride(engine.name, answer)
				if engine.type == "Solid":
					answer = query_min_max("What is the starting " + Fore.RED + "thrust for {}".format(engine.name) + Style.RESET_ALL, 0, float('inf'))
				self.HLV.setEngineAssignedThrustPerEngine("SRM", "max")



	def print_EdRow(self):
		edRow(
			bigG(self.HLV.get_V_horiz_mph(), self.HLV.get_OrbitalV()),
			self.HLV.get_V_vert_inc(),
			self.HLV.time,
			self.HLV.get_currentWeight(),
			self.HLV.get_A_total(),
			self.HLV.get_V_horiz_mph(),
			self.HLV.get_airSpeed(),
			self.HLV.get_A_vert_eff(),
			self.HLV.get_A_horiz(),
			self.HLV.get_V_vert(),
			self.HLV.get_alt(),
			self.HLV.getTotalThrust(),
			self.HLV.get_ADC_predicted(),
			self.HLV.get_ADC_actual(),
			self.HLV.get_ADC_adjusted(),
			self.HLV.get_A_total_eff()

		)


	def predict_ADC(self, rocket, events, assigned_V):
		threshold = 0.0000001
		ADC_error = 100000.0
		ADC_prediction = 0
		tries = 0
		while abs(ADC_error) > threshold:
			rocketCopy = copy.deepcopy(rocket)
			stopPrinting(lambda: self.compute_row(rocketCopy, events, ADC_prediction, assigned_V, False))
			ADC_error = rocketCopy.get_ADC_error()
			ADC_actual = rocketCopy.get_ADC_actual()
			#print ("Predicted ADC = {}\nerror={}\n=his prediction {}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, hisPredictedADC*10000.0, ADC_actual*10000.0))
			ADC_prediction -= ADC_error/2.0
			#print ("New Prediction = {}".format(ADC_prediction*10000.0))
			rocketCopy = None
			tries += 1
		return ADC_prediction

	def initialize_rocket(self):
		totalThrust = self.HLV.getTotalThrust()

		self.HLV.updateA()
		self.HLV.updateVertA(self.HLV.get_A_total_eff())
		self.HLV.update_V_vert()
		self.HLV.update_ADC_actual(self.HLV.time_inc)
		self.HLV.setEngineThrottle("RD-171M", "max", self.HLV.time_inc)
		self.HLV.burnFuel(self.HLV.time_inc)
		self.print_EdRow()
		self.HLV.set_time_inc()
		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):

		asssigned_vs = ["a", "a", "a", "a", "a", 0.55, 0.563, 0.56, 0.55, 0.55, 0.55, 0.515, 0.518, 0.51, 0.489, 0.495, 0.494, 0.510, 0.534, 0.560,
			0.570, 0.58, 0.59, 0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52, 0.51, 0.5, 0.5, 0.5, 0.48, 0.46, 0.44, 0.42, 0.3, 0.3, 0.3,
			0.3, 0.3, 0.221111032, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, -0.22, -0.44, -0.42, -0.4, -0.38, -0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22
			-0.20, -0.18, -0.16, -0.16, -0.13, -0.10, 0.012808983, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.20, -0.25, -0.40, -0.38,
			-0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18, -0.16, -0.14, -0.12, -0.10, -0.10, -0.10, -0.10, -0.10
		]



		i = 0

		# while HLV.get_V_horiz_mph() < self.COAST_SPEED
		while self.HLV.time <= 99:
			assigned_V = asssigned_vs[i]
			i += 1
			predictedADC = self.predict_ADC(self.HLV, self.events, assigned_V)
			self.compute_row(self.HLV, self.events, predictedADC, assigned_V) #returns time_inc

Rocketman = Main_program()
Rocketman.start()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
