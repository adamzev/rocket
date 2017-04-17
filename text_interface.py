from util import *
from title import *
from rocketEngine import *
from vehicle import *

def save_file(this_file):
	file_name = this_file['file_name']
	save_json(this_file, file_name)


def select_and_load_json_file(files):
	n = 1
	for this_file in files:
		file_data = load_json(this_file)
		print("{}) {}".format(n,file_data["friendly_name"]))
		n += 1
	file_num = query_int("Select a file number: ", None, 1, n-1)
	data = load_json(files[file_num-1])
	return data

def create_engine_specs():
	available_engines = Vehicle.load_available_engines()
	selected_engines = []
	for engine_name, engine_data in available_engines.iteritems():
		print("\n{}\n".format(engine_name))
		pretty_json(engine_data)
		attach = query_yes_no("Do you want to attach any {} engines? ".format(engine_name), None)
		if attach:
			count = query_float("How many?")
			engine_data["engine_count"] = count
			engine_data["engine_name"] = engine_name
			selected_engines.append(engine_data)
			print("{} {} engines are now attached.".format(int(count), engine_name))
	return selected_engines


def create_stage_specs(stage_type):
	stage_specs = {}
	stage_specs['attached'] = True
	stage_specs['adc_K'] = query_float("What is the ADC K of the {}?". format(stage_type))
	stage_specs['initial_weight'] = query_float("What is the lift-off weight of the {}? ".format(stage_type))
	stage_specs['jettison_weight'] = query_float("What is the jettison weight of the {}? ".format(stage_type))
	stage_specs['fuel'] = stage_specs['initial_weight'] - stage_specs['jettison_weight']
	stage_specs['type'] = stage_type
	print("Fuel available in {} is {}".format(stage_type, stage_specs['fuel']))
	return stage_specs


def create_stages_specs():
	attach_SRB = query_yes_no("Does the rocket have a SRB? ", "yes")
	stages = {}
	if attach_SRB:
		for stage_type in ["SRB", "RLV", "orbiter"]:
			stages[stage_type] = create_stage_specs(stage_type)
	else:
		for stage_type in ["RLV", "orbiter"]:
			stages[stage_type] = create_stage_specs()
		stages["SRB"] = {
			'adc_K' : 0.0,
			'attached' : False,
			'initial_weight' : 0.0,
			'jettison_weight' : 0.0,
			'fuel' : 0.0,
			'type' : "SRB"
		}
	return stages

def create_specs():
	name = raw_input("What is the vehicle called (for example: HLV * 4-8/6-9)? ")
	MK = raw_input("MK? ")
	ver = raw_input("Version? ")
	lift_off_weight = query_float("What is the weight at lift off? ")
	initial_alt = query_float("What is initial alt? ")
	A_hv_diff = query_float("What is desired A_h - A_v difference? ")
	tower_height = query_float("What is desired A_h - A_v difference? ")
	stages = create_stages_specs()
	selected_engines = create_engine_specs()
	friendly_name = "{} MK {} VER {}".format(n,spec_data["name"], spec_data["MK"], spec_data["ver"])
	clean_name = remove_non_alphanumeric(specs["name"]),
	clean_MK = remove_non_alphanumeric(specs["MK"]),
	clean_ver =  remove_non_alphanumeric(specs["ver"])
	file_name = "{}_MK_{}_VER_{}".format(n, clean_name, clean_MK, clean_ver)
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
		"engines" : selected_engines
	}

	save_settings = query_yes_no("Do you want to save these specs? ", None)
	if save_settings:
		save_specs(specs)
	return specs


def get_initial_conditions():
	return get_json_file_data("initial_conditions", "initial conditions", set_initial_conditions)



def get_specs():
	return get_json_file_data("specs", "spec", create_specs)

def get_json_file_data(folder, name, creation_function):
	files = glob.glob("{}/*.json".format(folder))
	if len(files) < 1: #if there are no spec files, you need to create one
		data = creation_function()
	else:
		create_new = query_yes_no("Do you want to create a new {} file? ".format(name), "no")
		if create_new:
			data = creation_function()
		else:
			data = select_and_load_json_file(files)

	pretty_json(data)
	return data
