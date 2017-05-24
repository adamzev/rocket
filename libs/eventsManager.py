''' query for flight profile information '''
from datetime import date
import time

from colorama import Fore, Back, Style

import libs.query as q
import libs.fileManager as fileMan

class EventManager(object):
	''' collect information regarding the flight profile (events that occur during the flight)
		for a given vehicle
	'''
	events = {}
	available_events = fileMan.load_json("save/events/events.json")["events"]

	def __init__(self, rocket):
		self.rocket = rocket
		self.collect_version()
		self.collect_starting_engine_settings()
		self.collect_launch_pad()
		self.collect_goals()
		self.select_from_list_of_available_events()


	def collect_launch_pad(self):
		''' queries and stores event info regarding the initial alt and tower height '''
		initial_alt = q.query_float("What is initial alt? ")
		tower_height = q.query_float("What is tower height?  ")
		self.events["initial_alt"] = initial_alt
		self.events["tower_height"] = tower_height


	def collect_goals(self):
		''' queries and stores the vertical velocity target '''
		V_v_target = q.query_float("What is desired V vert target (typically 2000fps)? ")
		self.events["V_v_target"] = V_v_target


	def collect_event_details(self, event):
		''' collect the requested fields for a given event object with keys:
			name: the name of the event
			duration_type: instant or interval
			data_needed: an array of objects
				field: name of the field needed
				type: 
					float, 
					string_from_list,
					array: just used for power down currently
					min_max_float: typically used to throttle (min 0.0, max 1.0)
					yes_no: get a bool
		 '''
		result = {}
		result["name"] = event["name"]
		print "\n", event["name"], "\n\n", event["description"], "\n"

		if event["duration_type"] == "instant":
			result["start_time"] = result["end_time"] = q.query_float("Event start time: ")
		else:
			result["start_time"] = q.query_float("Event start time: ")
			result["end_time"] = q.query_float("Event end time: ")

		for field in event["data_needed"]:
			field_name = field["field"]
			print(field_name)
			if field["type"] == "float":
				result[field_name] = q.query_float(field["prompt"])

			if field["type"] == "string_from_list":

				if field_name == "engine":
					engine_name = q.query_from_list("engine", "Select an engine: ", self.rocket.list_engine_names(), False)
					result[field_name] = engine_name

				if field_name == "stage":
					result[field_name] = q.query_from_list("stage", "Select a stage: ", self.rocket.stages.keys(), False)

			if field["type"] == "array":
				values = []
				for i in range(int(result["start_time"]), int(result["end_time"]) + 3, 3):
					values.append(q.query_float(field["prompt"]+str(i)+": "))
				result[field_name] = values

			if field["type"] == "min_max_float":
				result[field_name] = q.query_min_max(field["prompt"])

			if field["type"] == "yes_no":
				result[field_name] = q.query_yes_no(field["prompt"])

		print result
		return result

	def select_from_list_of_available_events(self):
		''' list the available events, select multiple and collect details about the events'''
		events = q.query_from_list("event", "Add events to the flight plan: ", self.available_events, True, self.collect_event_details)
		self.events["events"] = events

	def collect_version(self):
		''' get the version (used for the file name) '''
		today = date.fromtimestamp(time.time())
		self.events["friendly_name"] = q.query_string("What is the version date (hit enter for today's date)? ", today.strftime("%d-%m-%Y"))
		self.events["file_name"] = self.rocket.specs["file_name"] + "/events/" + self.events["friendly_name"]

	def collect_starting_engine_settings(self):
		''' collect the starting thrusts and throttles for the attached engines '''
		starting_thottles = []
		starting_thrusts = []

		for engine in self.rocket.engines:
			answer = q.query_min_max("What is the starting throttle for {} attached to the {}".format(engine.name, engine.stage))
			starting_thottles.append({"engine" : engine.name, "stage":engine.stage, "throt" : answer})
			if engine.type == "Solid":
				answer = q.query_min_max("What is the starting " + Fore.RED + "thrust per engine for {}".format(engine.name) + Style.RESET_ALL, 0, float('inf'))
				starting_thrusts.append({"engine" : engine.name, "stage":engine.stage, "thrust" : answer})

		self.events["starting_throt"] = starting_thottles
		self.events["starting_thrust"] = starting_thrusts
