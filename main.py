import math
import logging
import copy
import pprint
import sys
import mode

from generalEquations import *
from util.text_interface import *
from title import *
from libs import *
from libs.vehicleFactory import VehicleFactory

logging.basicConfig(level=logging.INFO)

class Main_program:
	def __init__(self, specs = []):
		self.messages = []
		self.specs = specs
		self.alt = 30.0
		self.COAST_SPEED = 16600
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
			self.HLV.V_v_target = event_file["V_v_target"]
			self.HLV.V_v_giveback_target = event_file["V_v_giveback_target"]

			self.HLV.ground_level = self.HLV.cur.alt
			self.HLV.tower_height = event_file["tower_height"]
		except IndexError:
			print("Initial alt, V_vert_target and giveback_target required in event file.")
			raise
		self.starting_thrust = event_file["starting_thrust"]
		self.starting_throt = event_file["starting_throt"]




	def compute_row(self, rocket, events, assigned_A_v, testRun=False):
		rocket.tick()

		rocket.burn_fuel(rocket.time_inc)
		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()
		self.check_for_event(events, rocket, True)
		if not mode.GIVEN_AVS:
			assigned_A_v = rocket.cur.A_vert_eff = rocket.select_A_vert()
		if assigned_A_v == "a" or assigned_A_v == "all":
			rocket.cur.A.vert = rocket.cur.A.total
			rocket.cur.A.horiz = 0.0
			rocket.cur.A.vert_eff = rocket.cur.A.vert - rocket.prev.big_G
		else:
			rocket.cur.A.vert = rocket.cur.A_vert_eff + rocket.prev.big_G
			try:
				rocket.cur.A.update(False, True, True)
			except ValueError:
				print("Invalid assigned A v. A v = {} A total = {}".format(rocket.cur.A.vert, rocket.cur.A.total))
				raise

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
		''' sets the initial thrusts and throttles of the engines '''
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
		ADC_prediction = rocket.cur.ADC_actual
		tries = 0
		while abs(ADC_error) > threshold:
			rocket_copy = copy.deepcopy(rocket)
			rocket_copy.cur.ADC_predicted = ADC_prediction
			self.compute_row(rocket_copy, events, assigned_V, False)
			#try:

			#except ValueError:
			#	ADC_error = 100000.0
			#	ADC_prediction = ADC_prediction / 2.0
			ADC_error = rocket_copy.cur.ADC_error
			ADC_actual = rocket_copy.cur.ADC_actual
			#print ("Predicted ADC = {}\nerror={}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, ADC_actual*10000.0))
			ADC_prediction -= ADC_error/2.0
			#print ("New Prediction = {}".format(ADC_prediction*10000.0))
			rocket_copy = None
			tries += 1
		return ADC_prediction

	def check_for_event(self, events, rocket, pre=False):
		if mode.GIVEN_INTERVALS:
			decimal_precision = 4
		else:
			if rocket.get_time_inc() == 0.1:
				decimal_precision = 1
			elif rocket.get_time_inc() == 0.01:
				decimal_precision = 2
			else:
				raise ValueError("Unsupported time inc")
		for event in events:
			preEvent = "pre" in event
			assert round(event["start_time"], decimal_precision) <= round(event["end_time"], decimal_precision)
			if (preEvent and pre) or (not preEvent and not pre): #is this a pre or post calculation event
				if round(event["start_time"], decimal_precision) <= round(rocket.time, decimal_precision) <= round(event["end_time"], decimal_precision):
					if "stage" in event.keys():
						rocket.handle_stage_event(event)
					elif "engine" in event.keys():
						rocket.handle_engine_event(event)
					else:
						rocket.handle_event(event)

	def add_unique_message(self, message):
		''' adds a message if it does not match the previous message '''
		if not self.messages or message != self.messages[-1]:
			self.messages.append(message)

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

		while self.HLV.cur.V.horiz_mph < self.COAST_SPEED:
			''' prints and clears the message queue '''
			for message in self.messages:
				print(message)

			self.messages = []
			if GIVEN_AVS:
				try:
					assigned_A_v = asssigned_vs[i]
				except IndexError:
					print "Sim complete"
					break
			else:
				assigned_A_v = None
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
				self.HLV.display_engine_messages()
				print(self.HLV)
				self.HLV.save_current_row()
			# self.HLV.fuel_used_per_stage_report()

print(TITLE)
Rocketman = Main_program()
Rocketman.set_initial_conditions()
Rocketman.initialize_rocket()
Rocketman.sim_rocket()
