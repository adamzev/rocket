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
		if QUICKRUN:
			self.HLV = Vehicle(self.specs, True)
		else:
			self.HLV = Vehicle(self.specs)


	def compute_row(self, rocket, events, assigned_A_v, testRun = False):
		for event in events:
			if rocket.time >= event["start_time"] and rocket.time <= event["end_time"]:
				if "stage" in event.keys():
					rocket.handle_stage_event(event)
				if "engine" in event.keys():
					rocket.handle_engine_event(event)
		rocket.tick()


		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()

		if assigned_A_v == "a" or assigned_A_v == "all":
			assigned_A_v = rocket.cur.A.total
			rocket.cur.A.horiz = 0.0
			rocket.cur.A.vert = assigned_A_v
		else:
			rocket.cur.A_vert_eff = float(assigned_A_v)
			rocket.cur.A.update(False, True, True)

		rocket.update_V_inc(rocket.time_inc)
		rocket.updateAlt(rocket.time_inc)
		rocket.cur.force = rocket.get_total_thrust()
		rocket.cur.V.horiz = rocket.prev.V.horiz + rocket.prev.V.horiz_inc
		rocket.cur.V.vert = rocket.prev.V.vert + rocket.cur.V.vert_inc

		#self.HLV.engine_status()
		#assigned_V = raw_input("Enter the assigned A_vert:")

		rocket.update_ADC_actual(rocket.time_inc)


		rocket.burnFuel(rocket.time_inc)



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
		threshold = 0.000001
		ADC_error = 100000.0
		ADC_prediction = 0.0
		tries = 0
		while abs(ADC_error) > threshold:
			rocketCopy = copy.deepcopy(rocket)
			rocketCopy.cur.ADC_predicted = ADC_prediction
			self.compute_row(rocketCopy, events, assigned_V, False)
			#try:

			#except ValueError:
			#	ADC_error = 100000.0
			#	ADC_prediction = ADC_prediction / 2.0
			ADC_error = rocketCopy.cur.ADC_error
			ADC_actual = rocketCopy.cur.ADC_actual
			#print ("Predicted ADC = {}\nerror={}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, ADC_actual*10000.0))
			ADC_prediction -= ADC_error/2.0
			#print ("New Prediction = {}".format(ADC_prediction*10000.0))
			rocketCopy = None
			tries += 1
		return ADC_prediction

	def initialize_rocket(self):
		self.HLV.prev.force = self.HLV.get_total_thrust()
		self.HLV.updateA()
		self.HLV.update_V_inc(self.HLV.time_inc)
		self.HLV.cur.A.vert = self.HLV.cur.A.total
		self.HLV.update_V_vert()
		self.HLV.update_ADC_actual(self.HLV.time_inc)

		self.HLV.setEngineThrottle("RD-171M", "max", self.HLV.time_inc)
		self.HLV.cur.force = self.HLV.get_total_thrust()
		self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, "a")
		print(self.HLV)
		self.HLV.save_current_row()
		self.HLV.burnFuel(self.HLV.time_inc)



		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):
		i = 0
		asssigned_vs = ["a", "a", "a", "a", "a", 0.55, 0.563, 0.56, 0.55, 0.55, 0.55, 0.515, 0.518, 0.51, 0.489, 0.495, 0.494, 0.510, 0.534, 0.560,
			0.570, 0.58, 0.59, 0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52, 0.51, 0.5, 0.5, 0.5, 0.48, 0.46, 0.44, 0.42, 0.3, 0.3, 0.3, 0.3,
			0.3, 0.3, 0.221111032, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, -0.22, -0.44, -0.42, -0.4, -0.38, -0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22
			-0.20, -0.18, -0.16, -0.16, -0.13, -0.10, 0.012808983, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.20, -0.25, -0.40, -0.38,
			-0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18, -0.16, -0.14, -0.12, -0.10, -0.10, -0.10, -0.10, -0.10
		]
		while self.HLV.cur.V.horiz_mph < self.COAST_SPEED:
			if QUICKRUN:
				assigned_A_v = asssigned_vs[i]
			else:
				assigned_A_v = self.HLV.select_A_vert()
			i += 1

			self.compute_row(self.HLV, self.events, assigned_A_v)
			self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, assigned_A_v)
			if round(self.HLV.time,1).is_integer():
				print(self.HLV)
				self.HLV.save_current_row()
				self.HLV.display_engine_messages()

Rocketman = Main_program()
Rocketman.start()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
