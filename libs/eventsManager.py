import libs.query as q
from datetime import date
import time
from colorama import Fore, Back, Style
from libs import Vehicle

class EventManager:
	events = {}
	available_events = [
		{
			"name" :"Set Throttle Target",
			"description": "Set the target throttle for all engines (regardless of stage) that match a name",
			"duration_type" : "interval",
			"data_needed": [
				{
					"field" : "engine",
					"type" : "string_from_list",
					"prompt" : "Select an engine from the list: "
				},
				{
					"field" : "target",
					"type" : "min_max_float",
					"prompt" : "Enter the target throttle: "
				}
			]
		},
		{
			"name" :"Set Throttle Target By Stage",
			"description": "Set the target throttle for all engines that match a name in a given stage",
			"duration_type" : "interval",
			"data_needed": [
				{
					"field" : "engine",
					"type" : "string_from_list",
					"prompt" : "Select an engine from the list: "
				},
				{
					"field" : "stage",
					"type" : "string_from_list",
					"prompt" : "Select a stage from the list: "
				},
				{
					"field" : "target",
					"type" : "min_max_float",
					"prompt" : "Enter the target throttle: "
				}
			]
		},
		{
			"name" :"Change Thrust",
			"description": "Change the thrust of a SRM by a given rate of change ",
			"duration_type" : "interval",
			"data_needed": [
				{
					"field" : "engine",
					"type" : "string_from_list",
					"prompt" : "Select an engine from the list: "
				},
				{
					"field" : "rate",
					"type" : "float",
					"prompt" : "Enter the change in thrust per second (use a negative number for a decrease)\n Thrust: "
				}
			]
		},
		{
			"name" :"Adjust Weight",
			"description": "This can be used to correct errors or to jettison parts other than the listed stages",
			"duration_type" : "instant",
			"data_needed": [
				{
					"field" : "amount",
					"type" : "float",
					"prompt" : "Enter the change in weight (use a negative number for a decrease) \n Weight: "
				},
				{
					"field" : "pre",
					"type" : "yes_no",
					"prompt" : "Enter the change to this row (rather than the next)?: "
				}
			]
		},
		{
			"name" : "Adjust Acceleration",
			"description": "This can be used to correct acceleration errors",
			"duration_type" : "instant",
			"data_needed": [
				{
					"field" : "amount",
					"type" : "float",
					"prompt" : "Enter the change in acceleration (use a negative number for a decrease)\nAcceleration: "
				},
				{
					"field" : "pre",
					"type" : "yes_no",
					"prompt" : "Enter the change to this row (rather than the next)?: "
				}
			]
		},
		{
			"name" :"Power Down Thrust",
			"description": "Power down a rocket engine based on thrust. This is only used for solid fueled boosters.",
			"duration_type" : "interval",
			"data_needed": [
				{
					"field" : "engine",
					"type" : "string_from_list",
					"prompt" : "Select an engine from the list: "
				},
				{
					"field" : "thrusts",
					"type" : "array",
					"prompt" : "Enter the thrusts in three second time intervals: "
				}
			]
		},
		{
			"name" :"Jettison",
			"description": "Jettison a stage.",
			"duration_type" : "instant",
			"data_needed": [
				{
					"field" : "stage",
					"type" : "string_from_list",
					"prompt" : "Select a stage from the list: "
				}
			]
		},

	]
	def __init__(self, rocket):
		self.rocket = rocket
		self.collect_version()
		self.collect_starting_engine_settings()
		self.collect_launch_pad()
		self.collect_A_v_goals()
		self.select_from_list_of_available_events()


	def collect_launch_pad(self):
		initial_alt = q.query_float("What is initial alt? ")
		tower_height = q.query_float("What is tower height?  ")
		self.events["initial_alt"] = initial_alt
		self.events["tower_height"] = tower_height


	def collect_A_v_goals(self):
		A_hv_diff = q.query_float("What is desired A_h - A_v difference? ")
		self.events["A_hv_diff"] = A_hv_diff


	def collect_event_details(self, event):
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
				for i in range(int(result["start_time"]), int(result["end_time"]), 3):
					values.append(q.query_float(field["prompt"]+str(i)+": "))
				result[field_name] = values

			if field["type"] == "min_max_float":
				result[field_name] = q.query_min_max(field["prompt"])

			if field["type"] == "yes_no":
				result[field_name] = q.query_yes_no(field["prompt"])

		print result
		return result

	def select_from_list_of_available_events(self):
		events = q.query_from_list("event", "Add events to the flight plan: ", self.available_events, True, self.collect_event_details)
		self.events["events"] = events

	def collect_version(self):
		today = date.fromtimestamp(time.time())
		self.events["friendly_name"] = q.query_string("What is the version date (hit enter for today's date)? ", today.strftime("%d-%m-%Y"))
		self.events["file_name"] = self.rocket.specs["file_name"] + "/events/" + self.events["friendly_name"]

	def collect_starting_engine_settings(self):
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
