import math
import logging
import copy
import pprint
from mode import *

from generalEquations import *
from text_interface import *
from util import *
from title import *

log = logging.basicConfig(level=logging.INFO)
class Main_program:
	def __init__(self, specs = []):
		self.specs = specs
		self.alt = 30.0
		self.COAST_SPEED = 166000
		self.endTime = 10.0

	def start(self):
		print(TITLE)
		self.specs = get_specs()
		#self.events = get_events()
		if QUICKRUN:
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
					"name" : "Power Down",
					"engine": "SRM",
					"start_time": 99.00,
					"end_time" : 114.00,
				},
				{
					"name" : "Jettison",
					"stage": "SRB",
					"start_time": 114.00,
					"end_time" : 114.00,
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


	def compute_row(self, rocket, events, predictedADC, assigned_A_v, printRow = True):
		rocket.set_ADC_predicted(predictedADC)

		for event in events:
			if rocket.time >= event["start_time"] and rocket.time <= event["end_time"]:
				if "stage" in event.keys():
					rocket.handle_stage_event(event)
				if "engine" in event.keys():
					rocket.handle_engine_event(event)
		rocket.tick()
		rocket.burnFuel(rocket.time_inc)

		#self.HLV.engine_status()


		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()
		print rocket.cur.A
		#assigned_V = raw_input("Enter the assigned A_vert:")

		if assigned_A_v == "a" or assigned_A_v == "all":
			assigned_A_v = rocket.cur.A.total_eff
			rocket.cur.A.vert = assigned_A_v
		else:
			rocket.cur.A.vert = float(assigned_A_v)
		print rocket.cur.A
		rocket.update_V(rocket.time_inc)

		rocket.update_ADC_actual(rocket.time_inc)


		if printRow:
			if round(rocket.time,1).is_integer():
				print(rocket)



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
					answer = query_min_max("What is the starting " + Fore.RED + "thrust per engine for {}".format(engine.name) + Style.RESET_ALL, 0, float('inf'))
				self.HLV.setEngineAssignedThrustPerEngine("SRM", "max")


	def predict_ADC(self, rocket, events, assigned_V):
		threshold = 0.0001
		ADC_error = 100000.0
		ADC_prediction = rocket.cur.ADC_actual
		tries = 0
		while abs(ADC_error) > threshold and tries < 20:
			rocketCopy = copy.deepcopy(rocket)

			try:
				stopPrinting(lambda: self.compute_row(rocketCopy, events, ADC_prediction, assigned_V, False))
			except:
				ADC_error = 100000.0
				ADC_prediction = ADC_prediction / 2.0
			ADC_error = rocketCopy.cur.ADC_error
			ADC_actual = rocketCopy.cur.ADC_actual
			#print ("Predicted ADC = {}\nerror={}\n=his prediction {}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, hisPredictedADC*10000.0, ADC_actual*10000.0))
			ADC_prediction -= ADC_error/2.0
			#print ("New Prediction = {}".format(ADC_prediction*10000.0))
			rocketCopy = None
			tries += 1
		return ADC_prediction

	def initialize_rocket(self):
		self.HLV.updateA()
		self.HLV.cur.A_vert = self.HLV.cur.A.total_eff
		self.HLV.update_V_vert()
		self.HLV.update_ADC_actual(self.HLV.time_inc)

		self.HLV.setEngineThrottle("RD-171M", "max", self.HLV.time_inc)
		print(self.HLV)
		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):
		i = 0

		while self.HLV.cur.V.horiz_mph < self.COAST_SPEED:
			assigned_A_v = self.HLV.select_A_vert()
			i += 1
			predictedADC = self.predict_ADC(self.HLV, self.events, assigned_A_v)
			self.compute_row(self.HLV, self.events, predictedADC, assigned_A_v)

Rocketman = Main_program()
Rocketman.start()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
