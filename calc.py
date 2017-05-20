from generalEquations import *
from libs.spec_creator import *
from libs.rocketEngine import *
from libs.stage import *
import libs.vehicle
import libs.vehicleFactory
import libs.velocity
import libs.query as q
import numpy as np


def prompt_thrust_at_alt():
	print "Thrust at alt Calculator"
	alt = float(raw_input("Alt? "))
	engines = libs.vehicleFactory.VehicleFactory.load_available_engines()
	engine_list = []
	n = 1
	for key, value in engines.iteritems():
		engine_list.append(value)
		print("{}) {}".format(n, key))
		n += 1

	engine_num = q.query_int("Select an engine number: ", None, 1, n-1)
	selected_engine = engine_list[engine_num-1]
	engine_num = q.query_int("How many? ", None, 1, 100)
	selected_engine["engine_count"] = engine_num
	engine = libs.rocketEngine.RocketEngine.factory(selected_engine)
	throt = q.query_min_max("Throttle? ")
	engine.setThrottleOverride(throt)
	engine.setThrottleOverride(throt)
	print engine.thrustAtAlt(alt)


def prompt_PATM():
	print "Percent of Atm Pressure Calculator"
	alt = float(raw_input("Alt? "))
	print percentOfAtmosphericPressure(alt)

def prompt_vac():
	print "Percent of Atm Vac Calculator"
	alt = float(raw_input("Alt? "))
	print percentOfVac(alt)

def prompt_big_G():
	print "Big G Calculator"
	V_h = float(raw_input("Horizontal Velocity? "))
	alt = float(raw_input("Alt? "))
	print bigG(V_h, velocity.Velocity.get_orbital(alt))

def prompt_ADC():
	print "ADC Calculator"
	V_as = float(raw_input("Air Speed Velocity? "))
	alt = float(raw_input("Alt? "))
	adc_K = float(raw_input("ADC K? "))
	print ADC(V_as, alt, adc_K)


def prompt_row():
	first_row = {
		"alt" :
			[
				{"type" : "float"},
				{"promt": "Enter alt: "}
			],
		"prior_alt":
			[
				{"type" : "float"},
				{"prompt" : "Enter the prior alt: "}
			],
		"time_inc":
			[
				{"type" : "float"},
				{"prompt" : "Enter the time increment: "}
			],
		"adc_guess":
			[
				{"type" : "float"},
				{"prompt" : "Guess the ADC: "}
			],
		"thrust":
			[
				{"type" : "float"},
				{"prompt" : "Enter the thrust: "}
			],
		"weight":
			[
				{"type" : "float"},
				{"prompt" : "Enter the weight: "}
			],
		"error":
			[
				{"type" : "float"},
				{"prompt" : "Enter the prior error: "}
			],
		"A_v":
			[
				{"type" : "string"},
				{"prompt" : "Assign the A_v or enter \"a\" to assign all A to A_V: "}
			],
		"A_h_prior":
			[
				{"type" : "float"},
				{"prompt" : "Enter the prior A_h: "}
			],
		"V_h_prior":
			[
				{"type" : "float"},
				{"prompt" : "Enter the prior V_h: "}
			],
		"V_v_prior":
			[
				{"type" : "float"},
				{"prompt" : "Enter the prior V_v: "}
			]
	}
	loop_rows = {
		"time_inc":
			[
				{"type" : "float"},
				{"prompt" : "Enter the time increment: "}
			],
		"adc_guess":
			[
				{"type" : "float"},
				{"prompt" : "Guess the ADC: "}
			],
		"thrust":
			[
				{"type" : "float"},
				{"prompt" : "Enter the thrust: "}
			],
		"weight":
			[
				{"type" : "float"},
				{"prompt" : "Enter the weight: "}
			],
		"A_v":
			[
				{"type" : "string"},
				{"prompt" : "Assign the A_v or enter \"a\" to assign all A to A_V: "}
			]
		}

def prompt_preburn():
	spec_data = get_json_file_data("specs", "spec", create_specs)
	alt = q.query_float("What is the alt for the preburn? ")
	preburn = Stage({})
	engines = []
	engine_rows = VehicleFactory.load_engine_data(spec_data["engines"])
	for engine_row in engine_rows:
		engine = RocketEngine.factory(engine_row)
		engine.set_fuel_source(preburn)
		engines.append(engine)
		start_time = q.query_float("What is the {}'s start time (positive start times will be ignored for preburn)? ".format(engine.name))
		if start_time < 0:
			start_throt = q.query_min_max("What is the starting throttle for {}".format(engine.name))
			target_throt = q.query_min_max("What is the target throttle for {}".format(engine.name))
			# set each weight twice to set average weight
			engine.setThrottleOverride(start_throt)
			if engine.type == "Solid":
				start_thrust = q.query_min_max("What is the starting " + Fore.RED + "thrust for {}".format(engine.name) + Style.RESET_ALL, 0, float("inf"))
				start_thrust = q.query_min_max("What is the target " + Fore.RED + "thrust for {}".format(engine.name) + Style.RESET_ALL, 0, float("inf"))
				engine.set_assigned_thrust_per_engine(start_thrust)

	time_inc = 0.01
	for i in np.arange(0, abs(start_time), time_inc):
		for engine in engines:
			engine.burn_fuel(time_inc, alt)
			engine.setThrottle(target_throt, time_inc)

	total_burned = 0.0
	print preburn.fuel_used
	# select config file or select engines
	# ask for engine start times
	# for each engine preburn until time 0
	# report amount burned per engine group
	# report total burned