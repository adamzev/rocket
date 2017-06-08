''' Simulate a heavy lift vehicle '''
import sys
import os
import traceback
import logging
import datetime

import copy
import mode as mode

from generalEquations import *

from libs.query import Query as q
import util.title as title
import util.func as func


import libs.exceptions as exceptions
import libs.edit_json as edit_json
from libs.spec_manager import Spec_manager
from libs import fileManager as fileMan
from libs.vehicleFactory import VehicleFactory



import ctypes
import msvcrt
import subprocess

from ctypes import wintypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

SW_MAXIMIZE = 3

kernel32.GetConsoleWindow.restype = wintypes.HWND
kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
kernel32.GetLargestConsoleWindowSize.argtypes = (wintypes.HANDLE,)
user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)


import ctypes

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11

class COORD(ctypes.Structure):
	_fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CONSOLE_FONT_INFOEX(ctypes.Structure):
	_fields_ = [("cbSize", ctypes.c_ulong),
				("nFont", ctypes.c_ulong),
				("dwFontSize", COORD),
				("FontFamily", ctypes.c_uint),
				("FontWeight", ctypes.c_uint),
				("FaceName", ctypes.c_wchar * LF_FACESIZE)]

font = CONSOLE_FONT_INFOEX()
font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
font.nFont = 12
font.dwFontSize.X = 11
font.dwFontSize.Y = 18
font.FontFamily = 54
font.FontWeight = 400
font.FaceName = "Lucida Console"

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
ctypes.windll.kernel32.SetCurrentConsoleFontEx(
		handle, ctypes.c_long(False), ctypes.pointer(font))
def maximize_console(lines=None):
	fd = os.open('CONOUT$', os.O_RDWR)
	try:
		hCon = msvcrt.get_osfhandle(fd)
		max_size = kernel32.GetLargestConsoleWindowSize(hCon)
		if max_size.X == 0 and max_size.Y == 0:
			raise ctypes.WinError(ctypes.get_last_error())
	finally:
		os.close(fd)
	cols = max_size.X
	hWnd = kernel32.GetConsoleWindow()
	if cols and hWnd:
		if lines is None:
			lines = max_size.Y
		else:
			lines = max(min(lines, 9999), max_size.Y)
		subprocess.check_call('mode.com con cols={} lines={}'.format(
								cols, lines))
		user32.ShowWindow(hWnd, SW_MAXIMIZE)
maximize_console(9999)
logging.basicConfig(level=logging.INFO)

today = datetime.date.today().strftime("%B-%d-%Y")
logging.basicConfig(filename="log/"+today+".log", level=logging.DEBUG)
logging.debug("Started log")
class Main_program(object):
	''' Stores and runs sims on a rocket '''
	restart_menu = ["Restart", "Edit the specs", "Quit"]
	def __init__(self):
		''' initializes the main program '''
		self.messages = []
		self.alt = 30.0
		self.COAST_SPEED = 16600
		self.endTime = 10.0

		self.specs = Spec_manager.get_specs()
		assert self.specs is not False

		if mode.QUICKRUN:
			self.HLV = VehicleFactory.create_vehicle(self.specs, True)
		else:
			self.HLV = VehicleFactory.create_vehicle(self.specs)
		event_file = Spec_manager.get_events(self.specs["file_name"], self.HLV)
		self.events = event_file["events"]
		try:
			self.HLV.cur.alt = event_file["initial_alt"]
			self.HLV.V_v_target = event_file["V_v_target"]

			self.HLV.ground_level = self.HLV.cur.alt
			self.HLV.tower_height = event_file["tower_height"]
		except IndexError:
			print("Initial alt, V_vert_target and giveback_target required in event file.")
			raise
		self.starting_thrust = event_file["starting_thrust"]
		self.starting_throt = event_file["starting_throt"]




	def compute_row(self, rocket, events, assigned_A_v, testRun=False):
		''' sims the rocket over the course of one time increment '''
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

			ADC_error = rocket_copy.cur.ADC_error

			ADC_prediction -= ADC_error/2.0

			rocket_copy = None
			tries += 1
		return ADC_prediction

	@staticmethod
	def check_for_event(events, rocket, pre=False):
		''' takes in a event dict and a vehicle (and optionally whether this a pre or post computation event)
		checks if the current time increment matches with an event and passes to the correct handler
		'''
		if mode.GIVEN_INTERVALS:
			decimal_precision = 4
		else:
			if rocket.get_time_inc() == 0.1:
				decimal_precision = 1
			elif rocket.get_time_inc() == 0.01:
				decimal_precision = 2
			else:
				raise ValueError("Unsupported time inc")
		if not pre:
			rocket.auto_events()

		for event in events:
			preEvent = "pre" in event
			if round(event["start_time"], decimal_precision) > round(event["end_time"], decimal_precision):
				raise ValueError("End times for events can not be before start times. ")
			if (preEvent and pre) or (not preEvent and not pre): #is this a pre or post calculation event
				if func.between_floats(rocket.time, event["start_time"], event["end_time"], decimal_precision):
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
		''' sims the first time inc '''
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
		if mode.QUICKRUN:
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
			# prints and clears the message queue
			for message in self.messages:
				print(message)

			self.messages = []
			if mode.GIVEN_AVS:
				try:
					assigned_A_v = asssigned_vs[i]
				except IndexError:
					print "Sim complete"
					break
			else:
				assigned_A_v = None
			i += 1

			self.compute_row(self.HLV, self.events, assigned_A_v)
			if mode.GIVEN_GUESSES:
				try:
					self.HLV.cur.ADC_predicted = predictedADCs.pop(0)
				except IndexError:
					self.HLV.cur.ADC_predicted = 0.0
			else:
				self.HLV.cur.ADC_predicted = self.predict_ADC(self.HLV, self.events, assigned_A_v)
			if mode.GIVEN_INTERVALS or round(self.HLV.time, 1).is_integer():
				self.HLV.display_engine_messages()
				print(self.HLV)
				self.HLV.save_current_row()
			# self.HLV.fuel_used_per_stage_report()


	def start(self):
		''' start the simulation '''
		self.set_initial_conditions()
		self.initialize_rocket()
		self.sim_rocket()



def restart_menu(last_spec_file):
	selection = q.query_from_list("option", "Select an option:", Main_program.restart_menu, False)
	if selection == "Restart":
		main()
	elif selection == "Edit the specs":
		Spec_manager.change_specs(fileMan.load_json(last_spec_file+".json"))
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
				print "\nSorry, an error has occured. \n\nPlease email the following information to Adam (Adam@TutorDelphia.com) if modifying the spec or event file will not fix the error.\n"
				print sys.exc_info()[0].__name__, os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename), sys.exc_info()[2].tb_lineno
				print e.__doc__
				print e.message
				print("An error has occured.")
				if mode.RESTART_ON_ERROR:
					restart_menu(Rocketman.specs["file_name"])
				else:
					raw_input("Press enter to quit")
					exit()
			else:
				raise type(e), type(e)(e.message), sys.exc_info()[2]
		else:
			restart_menu(Rocketman.specs["file_name"])
if __name__ == "__main__":
	main()
