import util.func as func
from libs.vehicleFactory import VehicleFactory
import libs.query as q
import libs.fileManager as fileMan
from libs.eventsManager import EventManager



def create_stage_specs(stage_type, fuel_type):
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
	event_man = EventManager(rocket)

	events = event_man.events
	save_settings = q.query_yes_no("Do you want to save these events? ", "yes")
	if save_settings:
		fileMan.save_file(events)

	return events
	# start a menu that lists supported events
	# add a submenu of engines that the event can be applied to
	# query for details (start, end, target)

def create_stages_specs():
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

def create_specs():
	name = q.query_string("What is the vehicle called (for example: HLV * 4-8/6-9)? ")
	MK = q.query_string("MK? ", "1")
	lift_off_weight = q.query_float("What is the weight at lift off? ")
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

	save_settings = q.query_yes_no("Do you want to save these specs? ", "yes")
	if save_settings:
		fileMan.save_file(specs)
	return specs

def change_specs(spec):
	''' Change the spec of a saved engine file '''
	def change_engines():
		''' Add or remove engines from a spec file '''
		chosen_stage = q.query_from_list("option", "Choose a stage:", [stage for stage in spec["stages"]], False)
		chosen = q.query_from_list("option", "Add or remove?", ["Add", "Remove"], False)
		if (chosen == "Add"):
			selected_engines = []
			selected_engines += VehicleFactory.select_engines(chosen_stage, spec["stages"][chosen_stage]["fuel_type"])
			spec["engines"] += selected_engines
		if (chosen == "Remove"):
			q.query_from_list(
				"option",
				"Choose an engine to remove?",
				[engine["engine_name"] for engine in spec["engines"] if engine["stage"] == chosen_stage],
				False
			)

	spec_functions = {
		"name": lambda: q.query_string("What is the vehicle called (for example: HLV * 4-8/6-9)? "),
		"MK": lambda: q.query_string("MK? ", "1"),
		"lift_off_weight": lambda: q.query_float("What is the weight at lift off? "),
		"stages": create_stages_specs,
		"engines": change_engines,
		"earth_rotation_mph": lambda: q.query_float("earth rotation mph? ")
	}
	spec_options = ["name", "MK", "lift_off_weight", "stages", "engines", "earth_rotation_mph"]

	change_another_property = True
	while (change_another_property):
		chosen_key = q.query_from_list("option", "Choose a property to change:", spec_options, False)
		spec_functions[chosen_key]()

		change_another_property = q.query_yes_no("Change another property?")

def get_initial_conditions():
	return fileMan.get_json_file_data("initial_conditions", "initial conditions", set_initial_conditions)

def get_events(spec_name, rocket):
	folder = spec_name + "/events"
	return fileMan.get_json_file_data(folder, "events", lambda: create_events(rocket))

def get_specs():
	return fileMan.get_json_file_data("save/specs", "spec", create_specs)
