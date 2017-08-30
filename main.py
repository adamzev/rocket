''' Simulate a heavy lift vehicle '''
import sys
import os
import traceback
import logging
import datetime

import copy
import mode as mode

from generalEquations import *



sys.path.append('/home/tutordelphia/www/rocket/')

import libs.exceptions as exceptions
import libs.edit_json as edit_json
from libs.spec_manager import Spec_manager
from libs import fileManager as fileMan
from libs.vehicleFactory import VehicleFactory


from libs.query import Query as q
import util.title as title
import util.func as func


today = datetime.date.today().strftime("%B-%d-%Y")
logging.basicConfig(filename="log/"+today+".log", level=logging.DEBUG)
logging.debug("Started log")
class Main_program(object):
	''' Stores and runs sims on a rocket '''
	def __init__(self):
		''' initializes the main program '''
		self.messages = []
		self.alt = 30.0
		self.coast_speed = 17050
		self.endTime = 10.0

		self.specs = Spec_manager.get_specs()
		assert self.specs is not False

		self.manual_Av = False
		self.manual_Av_frequency = None
		print('\n\nSpecs are loaded. Starting launch. Set launch options. \n\n')

		self.coast_speed = q.query_float(f"Enter the speed at which to end the simulation (or hit enter to select the default speed of {self.coast_speed}): ", self.coast_speed)

		self.A_vh_scale_factor = q.query_float("What is the A_vh scale factor (default is 1.0)? ", 1.0)

		self.change_weight = q.query_yes_no(f"The weight of the orbiter is {self.specs['stages']['orbiter']['initial_weight']}. \nThe lift-off-weight of the HLV is {self.specs['lift_off_weight']}. \nDo you want to change the orbiter? ", "no")
		if self.change_weight:
			self.specs['stages']['orbiter'] = Spec_manager.create_stage_specs("orbiter", "liquid")
			self.specs['lift_off_weight'] = self.HLV.sum_stage_weights()
			self.specs['MK'] = q.query_string("What is the MK? ")
			self.specs['friendly_name'] = "{} MK {}".format(self.specs['name'], self.specs['MK'])
			clean_name = func.remove_non_alphanumeric(self.specs['name'])
			clean_MK = func.remove_non_alphanumeric(self.specs['MK'])
			self.specs['file_name'] = "save/specs/{}_MK_{}".format(clean_name, clean_MK)

			version = VehicleFactory.collect_version()
			self.specs['friendly_name'] += " " + version['version_name']
			fileMan.ask_to_save(self.specs, "Do you want to save these specs? ")

		if mode.QUICKRUN:
			self.HLV = VehicleFactory.create_vehicle(self.specs, True)
		else:
			self.HLV = VehicleFactory.create_vehicle(self.specs)
		try:
			self.HLV.cur.alt = self.specs["initial_alt"]
			self.HLV.V_v_target = self.specs["V_v_target"]
			self.HLV.A_vh_scale_factor = self.A_vh_scale_factor
			self.HLV.V_v_giveback_target = self.specs["V_v_giveback_target"]
			self.HLV.V_v_giveback_time = round(self.specs["V_v_giveback_time"], 1)

			self.HLV.ground_level = self.HLV.cur.alt
			self.HLV.tower_height = self.specs["tower_height"]
		except IndexError:
			print("Initial alt, V_vert_target and giveback_target required in spec file.")
			raise




	def compute_row(self, rocket, assigned_A_v, testRun=False):
		''' sims the rocket over the course of one time increment '''
		rocket.tick()

		rocket.burn_fuel(rocket.time_inc)
		rocket.updateWeight(rocket.time_inc)
		rocket.updateA()
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

		rocket.events()

		rocket.cur.force = rocket.get_total_thrust()
		rocket.cur.set_big_G()

		#assigned_V = raw_input("Enter the assigned A_vert:")

		rocket.update_ADC_actual(rocket.time_inc)


	def set_initial_conditions(self):
		''' sets the initial thrusts and throttles of the engines '''
		engines = self.specs["engines"]
		for engine in engines:
			if "starting_throttle" in engine:
				self.HLV.setEngineThrottleOverride(
					engine["engine_name"], engine["starting_throttle"]
				)
				self.HLV.setEngineThrottleOverride(
					engine["engine_name"], engine["starting_throttle"]
				)

			if engine["engine_name"] == "SRM":
				self.HLV.setEngineAssignedThrustPerEngine("SRM", 3600000)
				self.HLV.setEngineAssignedThrustPerEngine("SRM", 3600000)
			if engine["engine_name"] == "SRMU":
				self.HLV.setEngineAssignedThrustPerEngine("SRMU", 1700000)
				self.HLV.setEngineAssignedThrustPerEngine("SRMU", 1700000)


	def predict_ADC(self, rocket, assigned_V):
		''' returns a ADC prediction based on test runs of different ADC values '''
		threshold = 0.000001
		ADC_error = 100000.0
		ADC_prediction = rocket.cur.ADC_actual
		tries = 0
		min_ADC = 0
		max_ADC = rocket.cur.ADC_actual * 5.0

		while abs(ADC_error) > threshold:
			rocket_copy = VehicleFactory.create_vehicle_copy(rocket)
			rocket_copy.cur.ADC_predicted = ADC_prediction
			try:
				self.compute_row(rocket_copy, assigned_V, False)
			except ValueError:
				# value error occurs when the ADC is too big (causing sqrt of neg)
				max_ADC = ADC_prediction
				ADC_prediction = (min_ADC + max_ADC) / 2.0
			else:
				if ADC_error < 0:
					min_ADC = ADC_prediction
				ADC_error = rocket_copy.cur.ADC_error
				ADC_prediction -= ADC_error

			rocket_copy = None
			tries += 1
			if tries > 20:
				threshold *= 10
				if threshold > 0.001:
					raise ValueError("An error occured while predicting ADC")
		return ADC_prediction


	def add_unique_message(self, message):
		''' adds a message if it does not match the previous message '''
		if not self.messages or message != self.messages[-1]:
			self.messages.append(message)

	def initialize_rocket(self):
		''' sims the first time inc '''
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

		self.HLV.events()

		self.HLV.cur.force = self.HLV.get_total_thrust()
		self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, "a")
		print(self.HLV)
		#self.HLV.display_engine_messages()
		self.HLV.save_current_row(True)




		#time_inc = float(raw_input("Enter the time inc:"))

	def sim_rocket(self):
		''' Main function for conducting a rocket simulation '''
		i = 0

		while self.HLV.cur.V.horiz_mph < self.coast_speed:
			# prints and clears the message queue
			for message in self.messages:
				print(message)

			self.messages = []
			if mode.GIVEN_AVS:
				try:
					assigned_A_v = asssigned_vs[i]
				except IndexError:
					print("Sim complete")
					break
			else:
				assigned_A_v = None
			i += 1

			self.compute_row(self.HLV, assigned_A_v)
			if mode.GIVEN_GUESSES:
				try:
					self.HLV.cur.ADC_predicted = predictedADCs.pop(0)
				except IndexError:
					self.HLV.cur.ADC_predicted = 0.0
			else:
				self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, assigned_A_v)
			if mode.GIVEN_INTERVALS or round(self.HLV.time, 1).is_integer():
				#self.HLV.display_engine_messages()
				print(self.HLV)
				self.HLV.save_current_row()
			# self.HLV.fuel_used_per_stage_report()


	def start(self):
		''' start the simulation '''
		self.set_initial_conditions()
		self.initialize_rocket()
		self.sim_rocket()



def restart_menu(last_spec_file=None):
	if last_spec_file:
		restart_menu_options = ["Restart", "Quit"]
	else:
		restart_menu_options = ["Restart", "Quit"]
	selection = q.query_from_list("option", "Select an option:", restart_menu_options, False)
	if selection == "Restart":
		main()
	elif selection == "Quit":
		exit()
	else:
		print("Unknown selection")

def main():
	while True:
		try:
			print(title.TITLE)
			Rocketman = Main_program()
			#restart_menu(Rocketman.specs["file_name"])
			Rocketman.start()

		except exceptions.FuelValueError:
			print("A stage ran out of fuel prior to jettisioning. Consider modifying the events.")
			restart_menu(Rocketman.specs["file_name"])
		# Catching all errors before exiting or allowing the user to try to fix the error
		except Exception as e: #pylint: disable=W0703
			if mode.PRETTY_ERRORS:
				print("\nSorry, an error has occured. \n\nPlease email the following information to Adam (Adam@TutorDelphia.com) if modifying the spec or event file will not fix the error.\n")
				print(sys.exc_info()[0].__name__, os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename), sys.exc_info()[2].tb_lineno)
				print(e.__doc__)
				print(e.message)
				print("An error has occured.")
				if mode.RESTART_ON_ERROR:
					if Rocketman:
						restart_menu(Rocketman.specs["file_name"])
					else:
						restart_menu()
				else:
					raw_input("Press enter to quit")
					exit()
			else:
				raise
		else:
			if Rocketman:
				restart_menu(Rocketman.specs["file_name"])
			else:
				restart_menu()
if __name__ == "__main__":
	main()
