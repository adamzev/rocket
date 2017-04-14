from util import *
from title import *

def save_specs(specs):
	file_name = "specs/{}_MK_{}_VER_{}.json".format(
		remove_non_alphanumeric(specs["name"]),
		remove_non_alphanumeric(specs["MK"]),
		remove_non_alphanumeric(specs["ver"])
	)

	save_json(specs, file_name)

def load_specs():
	spec_files = glob.glob("specs/*.json")
	n = 1
	for spec_file in spec_files:
		spec_data = load_json(spec_file)
		print("{}) {} MK {} VER {}".format(n,spec_data["name"], spec_data["MK"], spec_data["ver"]))
		n += 1
	file_num = query_int("Select a file number: ", None, 1, n-1)
	specs = load_json(spec_files[file_num-1])
	return specs

def create_specs():
	name = raw_input("What is the vehicle called (for example: HLV * 4-8/6-9)? ")
	MK = raw_input("MK? ")
	ver = raw_input("Version? ")
	lift_off_weight = query_float("What is the weight at lift off? ")
	initial_alt = query_float("What is initial alt? ")
	RSRB = query_float("What is the ADC K of the R SRB? ")
	RDRLV = query_float("What is the ADC K of the RD/RD-RLV? ")
	orbiter = query_float("What is the ADC K of the orbiter? ")
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
	specs = {
		"name" : name,
		"MK" : MK,
		"ver" : ver,
		"lift_off_weight" : lift_off_weight,
		"initial_alt" : initial_alt,
		"ADC_K" : [
			{"R-SRB" : RSRB},
			{"RD/RD-RLV" : RDRLV},
			{"Orbiter" : orbiter}
		],
		"engines" : selected_engines
	}
	save_specs = query_yes_no("Do you want to save these specs? ", None)
	if save_specs:
		save_specs(specs)

def get_specs():
	create_new_specs = query_yes_no("Do you want to create a new spec file? ", "no")
	if create_new_specs:
		specs = create_specs()
	else:
		specs = load_specs()
	pretty_json(specs)
	return specs



def edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust, ADC_guess = 0.0, ADC_actual = 0.0, ADC_adj = 0.0, A_total_eff = 0.0):
	row1 = "-"*140 + "\n"
	row2 = "{:>46.6f}      {:>6.8f}     G={: <12.8f}\n".format(A_total_eff, ADC_actual, big_G)
	time_string = "{:<6.1f}".format(time)
	time_string = Fore.RED + time_string + Style.RESET_ALL
	row3 = "+{:<12.2f} {:5} WT={:<11.2f}->{:>9.6f}      {:<12.8f}   Vh={:<12.6f} Vas={:<12.3f}     {:<12.6f}-{:<10.8f}\n".format(
		V_vert_inc, time_string, totalWeight, totalA, ADC_adj, V_horiz, V_as, A_v, A_h
	)
	alt_string = "ALT={:<.1f}\'".format(alt)
	row4 = "{:<13.6f} {:<16} T={:<19.4f}  \"{:<.4f}\"\n".format(V_vert, alt_string, thrust, ADC_guess)
	print(row1+row2+row3+row4)
