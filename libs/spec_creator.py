''' create a json spec file regarding the specs of a heavy lift vehicle '''
from functools import partial
import util.func as func
from libs.vehicleFactory import VehicleFactory
from libs.query import Query as q
import libs.fileManager as fileMan
from libs.eventsManager import EventManager



def create_stage_specs(stage_type, fuel_type):
	''' query for stage specs '''
	stage_specs = {}
	stage_specs['attached'] = True
	stage_specs['adc_K'] = q.query_float("What is the ADC K of the {}?". format(stage_type))
	stage_specs['initial_weight'] = q.query_float("What is the weight of the {}? ".format(stage_type))
	stage_specs['preburned'] = q.query_float("How much weight was used during preburn from the {}? ".format(stage_type))
	stage_specs['lift_off_weight'] = stage_specs['initial_weight'] - stage_specs['preburned']

	print("The lift off weight is {}".format(stage_specs['lift_off_weight']))

	if(stage_type != "orbiter"):
		stage_specs['jettison_weight'] = q.query_float("What is the jettison weight of the {}? ".format(stage_type))
	else:
		stage_specs['jettison_weight'] = 0
	stage_specs['fuel'] = stage_specs['lift_off_weight'] - stage_specs['jettison_weight']
	stage_specs['name'] = stage_type
	stage_specs['fuel_type'] = fuel_type
	print("Fuel to be burned in {} is {}".format(stage_type, stage_specs['fuel']))
	return stage_specs

def create_events(rocket):
	''' create and save an event file '''
	event_man = EventManager(rocket) # queries for the events for rocket

	fileMan.ask_to_save(event_man.events, "Do you want to save these events? ")
	return event_man.events

def create_stages_specs():
	''' queries for stage specs '''
	stages = {}
	stage_types = ["RLV", "orbiter"]
	attach_SRB = q.query_yes_no("Does the rocket have a SRB? ", "yes")
	if attach_SRB:
		stage_types = ["SRB"] + stage_types
	attach_LFB = q.query_yes_no("Does the rocket have a LFB? ", "no")
	if attach_LFB:
		stage_types = ["LFB"] + stage_types

	for stage_type in stage_types:
		if stage_type == "SRB":
			fuel_type = "Solid"
		else:
			fuel_type = "Liquid"
		stages[stage_type] = create_stage_specs(stage_type, fuel_type)
	return stages

query_vehicle_name = partial(q.query_string, "What is the vehicle called (for example: HLV * 4-8/6-9)? ")
query_vehicle_MK = partial(q.query_string, "MK? ", "1")
query_lift_off_weight = partial(q.query_float, "What is the weight at lift off? ")
query_earths_rotation = partial(
									q.query_float,
									"earth rotation mph (hit enter for the default value of 912.67)? ",
									912.67
								)
def create_specs():
	''' query for the specs for a heavy lift vehicle '''
	name = query_vehicle_name()
	MK = query_vehicle_MK()
	lift_off_weight = query_lift_off_weight()
	stages = create_stages_specs()

	selected_engines = []
	for stage_name, stage_data in stages.iteritems():
		print (stage_name)
		selected_engines += VehicleFactory.select_engines(stage_name, stage_data["fuel_type"])
	friendly_name = "{} MK {}".format(name, MK)
	clean_name = func.remove_non_alphanumeric(name)
	clean_MK = func.remove_non_alphanumeric(MK)
	file_name = "{}_MK_{}".format(clean_name, clean_MK)
	specs = {
		"name" : name,
		"MK" : MK,
		"friendly_name" : friendly_name,
		"file_name" : "save/specs/"+file_name,
		"lift_off_weight" : lift_off_weight,
		"stages" : stages,
		"engines" : selected_engines,
		"earth_rotation_mph" : 912.67
	}

	fileMan.ask_to_save(specs, "Do you want to save these specs? ")
	return specs

def change_specs(specs):
	''' Change the spec of a saved engine file '''
	def change_engines(specs):
		''' Add or remove engines from a specs file and returns the engine specs (not the whole spec file) '''
		chosen_stage = q.query_from_list("option", "Choose a stage:", [stage for stage in specs["stages"]], False)
		chosen = q.query_from_list("option", "Add or remove?", ["Add", "Remove"], False)
		if (chosen == "Add"):
			selected_engines = []
			selected_engines += VehicleFactory.select_engines(chosen_stage, specs["stages"][chosen_stage]["fuel_type"])
			specs["engines"] += selected_engines
		if (chosen == "Remove"):
			selected_engine = q.query_from_list(
				"option",
				"Choose an engine to remove?",
				[engine["engine_name"] for engine in specs["engines"] if engine["stage"] == chosen_stage],
				False
			)
			del specs["engines"][selected_engine]
		return specs["engines"]

	spec_functions = {
		"name": query_vehicle_name,
		"MK": query_vehicle_MK,
		"lift_off_weight": query_lift_off_weight,
		"stages": create_stages_specs,
		"engines": lambda: change_engines(specs),
		"earth_rotation_mph": query_earths_rotation
	}

	change_another_property = True
	while (change_another_property):
		chosen_key = q.query_from_list("option", "Choose a property to change:", spec_functions.keys(), False)
		specs[chosen_key] = spec_functions[chosen_key]()

		change_another_property = q.query_yes_no("Change another property?")

	fileMan.ask_to_save(specs, "Do you want to save these changes? ")

def get_events(spec_name, rocket):
	''' load or create an event file '''
	folder = spec_name + "/events"
	return fileMan.get_json_file_data(folder, "events", lambda: create_events(rocket))

def get_specs():
	''' get specs by asking the user to create them or select an existing file from a list '''
	return fileMan.get_json_file_data("save/specs", "spec", create_specs)
