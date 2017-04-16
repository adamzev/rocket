from util import *
from title import *
from rocketEngine import *
from vehicle import *

def save_specs(specs):
	file_name = "specs/{}_MK_{}_VER_{}.json".format(
		remove_non_alphanumeric(specs["name"]),
		remove_non_alphanumeric(specs["MK"]),
		remove_non_alphanumeric(specs["ver"])
	)

	save_json(specs, file_name)

def load_specs(spec_files):
	n = 1
	for spec_file in spec_files:
		spec_data = load_json(spec_file)
		print("{}) {} MK {} VER {}".format(n,spec_data["name"], spec_data["MK"], spec_data["ver"]))
		n += 1
	file_num = query_int("Select a file number: ", None, 1, n-1)
	specs = load_json(spec_files[file_num-1])
	return specs

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
	stages = create_stages_specs()
	selected_engines = create_engine_specs()

	specs = {
		"name" : name,
		"MK" : MK,
		"ver" : ver,
		"lift_off_weight" : lift_off_weight,
		"initial_alt" : initial_alt,
		"stages" : stages,
		"engines" : selected_engines
	}

	save_settings = query_yes_no("Do you want to save these specs? ", None)
	if save_settings:
		save_specs(specs)
	return specs



def get_specs():
	spec_files = glob.glob("specs/*.json")
	if len(spec_files) >= 1:
		create_new_specs = query_yes_no("Do you want to create a new spec file? ", "no")
		if create_new_specs:
			specs = create_specs()
		else:
			specs = load_specs(spec_files)
	else:
		specs = create_specs() #if there are no spec files, you need to create one
	pretty_json(specs)
	return specs
