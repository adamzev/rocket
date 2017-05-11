import math
import logging
import copy
import pprint
import sys
from mode import *

from generalEquations import *
from util.text_interface import *
from title import *
from libs import *
from libs.vehicleFactory import VehicleFactory

logging.basicConfig(level=logging.INFO)

class Main_program:
	def __init__(self, specs = []):
		self.specs = specs
		self.alt = 30.0
		self.COAST_SPEED = 166000
		self.endTime = 10.0

		self.specs = get_specs()
		assert self.specs is not False

		if QUICKRUN:
			self.HLV = VehicleFactory.create_vehicle(self.specs, True)
		else:
			self.HLV = VehicleFactory.create_vehicle(self.specs)
		event_file = get_events(self.specs["file_name"], self.HLV)
		self.events = event_file["events"]
		try:
			self.HLV.cur.alt = event_file["initial_alt"]
			self.HLV.ground_level = self.HLV.cur.alt
			self.HLV.tower_height = event_file["tower_height"]
		except IndexError:
			sys.exit("Initial alt required in event file.")
		self.starting_thrust = event_file["starting_thrust"]
		self.starting_throt = event_file["starting_throt"]




	def compute_row(self, rocket, events, assigned_A_v, testRun=False):
		rocket.tick()

		rocket.burn_fuel(rocket.time_inc)
		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()
		self.check_for_event(events, rocket, True)
		if assigned_A_v == "a" or assigned_A_v == "all":
			rocket.cur.A.vert = rocket.cur.A.total
			rocket.cur.A.horiz = 0.0
			rocket.cur.A.vert_eff = rocket.cur.A.vert - rocket.prev.big_G

		else:
			rocket.cur.A_vert_eff = float(assigned_A_v)
			rocket.cur.A.vert = assigned_A_v + rocket.prev.big_G
			try:
				rocket.cur.A.update(False, True, True)
			except ValueError:
				print("Invalid assigned A v")
				exit()

		rocket.update_V_inc(rocket.time_inc)
		rocket.cur.V.horiz = rocket.prev.V.horiz + rocket.cur.V.horiz_inc
		rocket.cur.V.vert = rocket.prev.V.vert + rocket.cur.V.vert_inc
		rocket.updateAlt(rocket.time_inc)

		self.check_for_event(events, rocket)

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
		''' returns a ADC prediction based on test runs of different ADC values '''
		threshold = 0.000001
		ADC_error = 100000.0
		ADC_prediction = 0.0
		tries = 0
		while abs(ADC_error) > threshold:
			rocket_copy = copy.deepcopy(rocket)
			rocket_copy.cur.ADC_predicted = ADC_prediction
			self.compute_row(rocket_copy, events, assigned_V, False)
			#try:

			#except ValueError:
			#	ADC_error = 100000.0
			#	ADC_prediction = ADC_prediction / 2.0
			#ADC_error = rocket_copy.cur.ADC_error
			#ADC_actual = rocket_copy.cur.ADC_actual
			#print ("Predicted ADC = {}\nerror={}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, ADC_actual*10000.0))
			#ADC_prediction -= ADC_error/2.0
			#print ("New Prediction = {}".format(ADC_prediction*10000.0))
			rocket_copy = None
			tries += 1
		return ADC_prediction

	def check_for_event(self, events, rocket, pre=False):
		for event in events:
			preEvent = "pre" in event
			if (preEvent and pre) or (not preEvent and not pre): #is this a pre or post calculation event
				if round(rocket.time, 4) >= event["start_time"] and round(rocket.time, 4) <= event["end_time"]:
					if "stage" in event.keys():
						rocket.handle_stage_event(event)
					if "engine" in event.keys():
						rocket.handle_engine_event(event)
					else:
						rocket.handle_event(event)

	def initialize_rocket(self):
		self.check_for_event(self.events, self.HLV, True)
		self.HLV.cur.set_big_G()
		self.HLV.prev = copy.deepcopy(self.HLV.cur)
		self.HLV.cur.set_big_G()
		self.HLV.prev.force = self.HLV.get_total_thrust()
		self.HLV.updateA()
		self.HLV.update_V_inc(self.HLV.time_inc)
		self.HLV.cur.A.vert = self.HLV.cur.A.total
		self.HLV.cur.set_big_G()
		self.HLV.cur.A.vert_eff = self.HLV.cur.A.vert - self.HLV.cur.big_G
		self.HLV.update_V_vert()
		self.HLV.update_ADC_actual(self.HLV.time_inc)

		self.check_for_event(self.events, self.HLV)

		self.HLV.cur.force = self.HLV.get_total_thrust()
		if QUICKRUN:
			self.HLV.cur.ADC_predicted = 0.00023
		else:
			self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, "a")
		print(self.HLV)
		self.HLV.display_engine_messages()
		self.HLV.save_current_row(True)




		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):
		''' Main function for conducting a rocket simulation '''
		i = 0
		asssigned_vs = ["a", "a", "a", "a", 0.580023, 0.555, 0.548, 0.535, 0.532, 0.524, 0.505, 0.49, 0.485, 0.48, 0.482, 0.49, 0.5,
			0.524, 0.550, 0.585, 0.622, 0.655, 0.679, 0.665, 0.695, 0.725, 0.740, 0.740, 0.73, 0.72, 0.72, 0.72, .7, 0.68, 0.59,
			0.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.08, 0.030147717, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
			0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
			0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, -0.4, -0.4, -0.39, -0.38, -0.37, -0.36, -0.35, -0.34, -0.33,
			-0.32, -0.31, -0.30, -0.29, -0.28, -0.27, -0.26, -0.26, -0.25, -0.24, -0.23, -0.22, -0.21, -0.2, -0.19, -0.18, -0.17, -0.16
			-0.15, -0.14, -0.13, -0.12, -0.12, -0.12, -0.12, -0.12, -0.12, -0.11, -0.10, -0.026826337, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
			0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
		]

		predictedADCs = [0.00079, 0.00285, 0.0142, 0.0328, 0.0611, 0.1000, 0.1546, 0.2021, 0.2582, 0.314, 0.368, 0.4164, 0.4616, 0.5010, 0.5353, 0.5635,
			0.5853, 0.6026, 0.6086, 0.6136, 0.6185, 0.592, 0.595, 0.5605, 0.5172, 0.4775, 0.4775, 0.4287, 0.374, 0.3467, 0.3167, 0.279, 0.2476, 0.2174,
			0.1894, 0.1642, 0.1424, 0.1237, 0.1074, 0.08978, 0.0815, 0.07162, 0.06283, 0.05383, 0.04916, 0.044155, 0.03816, 0.0365, 0.0360, 0.0346, 0.0331, 0.0331,

		]
		while self.HLV.cur.V.horiz_mph < self.COAST_SPEED:
			if GIVEN_AVS:
				try:
					assigned_A_v = asssigned_vs[i]
				except IndexError:
					print "Sim complete"
					break
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
			if GIVEN_INTERVALS or round(self.HLV.time, 1).is_integer():
				print(self.HLV)
				self.HLV.save_current_row()
				self.HLV.display_engine_messages()
			self.HLV.fuel_used_per_stage_report()

print(TITLE)
Rocketman = Main_program()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
