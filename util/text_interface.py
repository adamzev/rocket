from title import *
import libs.rocketEngine
from libs.vehicle import Vehicle
from libs.stage import Stage
import libs.query as q
import libs.fileManager as fileMan


def create_stage_specs(stage_type, fuel_type):
	stage_specs = {}
	stage_specs['attached'] = True
	stage_specs['adc_K'] = q.query_float("What is the ADC K of the {}?". format(stage_type))
	stage_specs['initial_weight'] = q.query_float("What is the weight of the {}? ".format(stage_type))
	if(stage_type != "orbiter"):
		stage_specs['jettison_weight'] = q.query_float("What is the jettison weight of the {}? ".format(stage_type))
	else:
		stage_specs['jettison_weight'] = 0
	stage_specs['fuel'] = stage_specs['initial_weight'] - stage_specs['jettison_weight']
	stage_specs['type'] = stage_type
	stage_specs['fuel_type'] = fuel_type
	print("Fuel available in {} is {}".format(stage_type, stage_specs['fuel']))
	return stage_specs

def create_events(rocket):

	starting_thottles = []
	starting_thrusts = []
	version = raw_input("What is the version date? ")
	for engine in rocket.engines:
		answer = q.query_min_max("What is the starting throttle for {} attached to the {}".format(engine.name, engine.stage))
		starting_thottles.append({"engine" : engine.name, "stage":engine.stage, "throt" : answer})
		if engine.type == "Solid":
			answer = q.query_min_max("What is the starting " + Fore.RED + "thrust per engine for {}".format(engine.name) + Style.RESET_ALL, 0, float('inf'))
			starting_thrusts.append({"engine" : engine.name, "stage":engine.stage, "thrust" : answer})
	events = {
		"file_name" : "save/specs/" + rocket.specs["file_name"] + "/events/" + version,
		"friendly_name" : version,
		"starting_throt" : starting_thottles,
		"starting_thrust" : starting_thrusts
	}

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
	name = raw_input("What is the vehicle called (for example: HLV * 4-8/6-9)? ")
	MK = raw_input("MK? ")
	ver = raw_input("Version? ")
	lift_off_weight = q.query_float("What is the weight at lift off? ")
	initial_alt = q.query_float("What is initial alt? ")
	A_hv_diff = q.query_float("What is desired A_h - A_v difference? ")
	tower_height = q.query_float("What is tower height?  ")
	stages = create_stages_specs()

	selected_engines = []
	for key, value in stages.iteritems():
		print "Select engines for stage {}".format(key)
		selected_engines += Stage.select_engines(value["fuel_type"])
	friendly_name = "{} MK {} VER {}".format(name, MK, ver)
	clean_name = remove_non_alphanumeric(name)
	clean_MK = remove_non_alphanumeric(MK)
	clean_ver =  remove_non_alphanumeric(ver)
	file_name = "{}_MK_{}_VER_{}".format(clean_name, clean_MK, clean_ver)
	specs = {
		"name" : name,
		"MK" : MK,
		"ver" : ver,
		"friendly_name" : friendly_name,
		"file_name" : file_name,
		"lift_off_weight" : lift_off_weight,
		"initial_alt" : initial_alt,
		"A_hv_diff" : A_hv_diff,
		"tower_height" : tower_height,
		"stages" : stages,
		"engines" : selected_engines,
		"earth_rotation_mph" : 912.67
	}

	save_settings = q.query_yes_no("Do you want to save these specs? ", "yes")
	if save_settings:
		fileMan.save_file(specs)
	return specs


def get_initial_conditions():
	return fileMan.get_json_file_data("initial_conditions", "initial conditions", set_initial_conditions)


def get_events(spec_name, rocket):
	folder = "save/specs/" + spec_name + "/events"
	return fileMan.get_json_file_data(folder, "events", lambda: create_events(rocket))

def get_specs():
	return fileMan.get_json_file_data("save/specs", "spec", create_specs)