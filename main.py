import math
import logging
import copy
import pprint
from mode import *

from generalEquations import *
from util import *
from util.text_interface import *
from title import *
from libs import *
from libs.vehicle import *

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
		if QUICKRUN:
			self.HLV = Vehicle(self.specs, True)
		else:
			self.HLV = Vehicle(self.specs)

		event_file = get_events(self.specs["file_name"], self.HLV)
		self.starting_thrust = event_file["starting_thrust"]
		self.starting_throt = event_file["starting_throt"]
		self.events = event_file["events"]
		# check if there is a event file of the same name prefix
		# ask to load or create new events
		# load event file selected




	def compute_row(self, rocket, events, assigned_A_v, testRun = False):
		rocket.tick()
		rocket.burn_fuel(rocket.time_inc)
		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()

		if assigned_A_v == "a" or assigned_A_v == "all":
			rocket.cur.A.vert = rocket.cur.A.total
			rocket.cur.A.horiz = 0.0
			rocket.cur.A.vert_eff = rocket.cur.A.vert - rocket.prev.big_G

		else:
			rocket.cur.A_vert_eff = float(assigned_A_v)
			rocket.cur.A.vert = assigned_A_v + rocket.prev.big_G
			rocket.cur.A.update(False, True, True)

		rocket.update_V_inc(rocket.time_inc)
		rocket.cur.V.horiz = rocket.prev.V.horiz + rocket.cur.V.horiz_inc
		rocket.cur.V.vert = rocket.prev.V.vert + rocket.cur.V.vert_inc
		rocket.updateAlt(rocket.time_inc)

		for event in events:
			if rocket.time >= event["start_time"] and rocket.time <= event["end_time"]:
				if "stage" in event.keys():
					rocket.handle_stage_event(event)
				if "engine" in event.keys():
					rocket.handle_engine_event(event)

		rocket.cur.force = rocket.get_total_thrust()
		rocket.cur.set_big_G()
		#self.HLV.engine_status()
		#assigned_V = raw_input("Enter the assigned A_vert:")

		rocket.update_ADC_actual(rocket.time_inc)


	def set_initial_conditions(self):
		for eng_start in self.starting_throt:
			self.HLV.setEngineThrottleOverride(eng_start["engine"], eng_start["throt"])
			self.HLV.setEngineThrottleOverride(eng_start["engine"], eng_start["throt"])

		for eng_start in self.starting_thrust:
			self.HLV.setEngineAssignedThrustPerEngine(eng_start["engine"], eng_start["thrust"])
			self.HLV.setEngineAssignedThrustPerEngine(eng_start["engine"], eng_start["thrust"])


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
		self.HLV.cur.set_big_G()
		self.HLV.prev = copy.deepcopy(self.HLV.cur)
		self.cur = PhysicalStatus()
		self.HLV.cur.set_big_G()
		self.HLV.prev.force = self.HLV.get_total_thrust()
		self.HLV.updateA()
		self.HLV.update_V_inc(self.HLV.time_inc)
		self.HLV.cur.A.vert = self.HLV.cur.A.total
		self.HLV.cur.set_big_G()
		self.HLV.cur.A.vert_eff = self.HLV.cur.A.vert - self.HLV.cur.big_G
		self.HLV.update_V_vert()
		self.HLV.update_ADC_actual(self.HLV.time_inc)

		for event in self.events:
			if self.HLV.time >= event["start_time"] and self.HLV.time <= event["end_time"]:
				if "stage" in event.keys():
					self.HLV.handle_stage_event(event)
				if "engine" in event.keys():
					self.HLV.handle_engine_event(event)

		self.HLV.cur.force = self.HLV.get_total_thrust()
		if QUICKRUN:
			self.HLV.cur.ADC_predicted = 0.00012
		else:
			self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, "a")
		print(self.HLV)
		self.HLV.save_current_row(True)




		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):
		i = 0
		asssigned_vs = ["a", "a", "a", "a", "a", 0.55, 0.563, 0.56, 0.55, 0.55, 0.55, 0.515, 0.518, 0.51, 0.489, 0.495, 0.494, 0.510, 0.534, 0.560,
			0.570, 0.58, 0.59, 0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52, 0.51, 0.5, 0.5, 0.5, 0.48, 0.46, 0.44, 0.42, 0.3, 0.3, 0.3, 0.3,
			0.3, 0.3, 0.221111032, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, -0.22, -0.44, -0.42, -0.4, -0.38, -0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22
			-0.20, -0.18, -0.16, -0.16, -0.13, -0.10, 0.012808983, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.20, -0.25, -0.40, -0.38,
			-0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18, -0.16, -0.14, -0.12, -0.10, -0.10, -0.10, -0.10, -0.10
		]

		predictedADCs = [0.00086, 0.0022, 0.0043, 0.01106, 0.0268, 0.0448, 0.0777, 0.127, 0.171, 0.2148, 0.2798, 0.3239, 0.3615, 0.4135, 0.4497, 0.487,
		0.5109, 0.5284, 0.5370, 0.5540, 0.5533, 0.5555, 0.5515, 0.5376, 0.5222, 0.5016, 0.4678, 0.4739, 0.4359, 0.4089, 0.3864, 0.356, 0.3248, 0.2945,
		0.2725, 0.239, 0.211, 0.184, 0.156, 0.131, 0.131, 0.0932, 0.0793, 0.06756, 0.0587, 0.04904, 0.04285, 0.03535, 0.03295, 0.03085, 0.0296, 0.02785,
		0.02756, 0.02596, 0.02284, 0.01744, 0.01363, 0.011103, 0.0091, 0.007155, 0.00605, 0.004758, 0.003829, 0.003124, 0.002476, 0.002020, 0.001613, 0.001284,
		0.001284, 0.001038, 0.0008304, 0.000654, 0.00052, 0.0004133, 0.000326, 0.000254, 0.000197, 0.00001527, 0.000114, 0.000112, 0.000089, 0.000091739, 0.0000817, 0.0000817, 0.000022, 0.0000156,
		0.0000102, 0.000007344, 0.00000451, 0.000003015, 0.000001269, 0.00000079

	]
		while self.HLV.cur.V.horiz_mph < self.COAST_SPEED:
			if GIVEN_AVS:
				assigned_A_v = asssigned_vs[i]
			else:
				assigned_A_v = self.HLV.select_A_vert()
			i += 1

			self.compute_row(self.HLV, self.events, assigned_A_v)
			if GIVEN_GUESSES:
				try:
					self.HLV.cur.ADC_predicted = predictedADCs.pop(0)
				except IndexError:
					self.HLV.cur.ADC_predicted = 0.0
			else:
				self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, assigned_A_v)
			if GIVEN_INTERVALS or round(self.HLV.time,1).is_integer():
				print(self.HLV)
				self.HLV.save_current_row()
				self.HLV.display_engine_messages()

Rocketman = Main_program()
Rocketman.start()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
