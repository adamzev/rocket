import math
import logging
import copy
import pprint

from rocketEngine import *
from vehicle import *
from generalEquations import *

from util import *

log = logging.basicConfig(level=logging.INFO)

create_new_specs = query_yes_no("Do you want to create a new spec file? ", "no")
if create_new_specs:
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
		file_name = "{}_MK_{}_VER_{}".format(
			remove_non_alphanumeric(specs["name"]),
			remove_non_alphanumeric(specs["MK"]),
			remove_non_alphanumeric(specs["ver"])
		)

		save_json(specs, file_name)

else:
	spec_files = glob.glob("specs/*.json")
	n = 1
	for spec_file in spec_files:
		spec_data = load_json(spec_file)
		print("{}) {} MK {} VER {}".format(n,spec_data["name"], spec_data["MK"], spec_data["ver"]))
		n += 1
	file_num = query_int("Select a file number: ", None, 1, n-1)
	specs = load_json(spec_files[file_num-1])


pretty_json(specs)
events = [
	{
		"name" : "Increase Throttle By Max Rate-Of-Change",
		"engine": "RD-171M",
		"start_time": 0.00,
		"end_time" : 3.00,
	},
	{
		"name" : "Reduce Thrust",
		"engine": "SRM",
		"start_time": 24.00,
		"end_time" : 45.00,
		"rate" : -20000.0,
	},
	{
		"name" : "Reduce Thrust Until Depleted",
		"engine": "SRM",
		"start_time": 102.00,
		"end_time" : 114.00,
	},
	{
		"name" : "Jettison",
		"engine": "SRM",
		"start_time": 114.10,
		"end_time" : 114.10,
	},
	{
		"name" : "Reduce Throttle By Max Rate-Of-Change",
		"engine": "RD-171M",
		"start_time": 137.00,
		"end_time" : 140.00,
	},
	{
		"name" : "Engine Cut-off",
		"engine": "RD-171M",
		"start_time": 140.00,
		"end_time" : 140.00,

	}
]


HLV = Vehicle(specs)


def compute_row(rocket, time, time_inc, time_incs, events, predictedADC, assigned_V, printRow = True):
	rocket.set_ADC_predicted(predictedADC)
	print time_inc
	for event in events:
		if time >= event["start_time"] and time <= event["end_time"]:
			rocket.handle_event(event, time, time_inc)

	#HLV.engine_status()

	rocket.updateWeight(time_inc)
	rocket.updateA()
	#assigned_V = raw_input("Enter the assigned A_vert:")


	if assigned_V == "a" or assigned_V == "all":
		assigned_V = rocket.get_A_total_eff()
		rocket.updateVertA(assigned_V)
	else:
		assigned_V = float(assigned_V)
		rocket.updateVertA(assigned_V, False)



	rocket.updateHorizA()
	rocket.update_V(time_inc)
	rocket.updateAlt(time_inc)
	rocket.update_ADC_actual(time_inc)
	for timeIncrements in time_incs:
		if time<timeIncrements["until"]:
			time_inc = timeIncrements["time_inc"]
			break
	rocket.burnFuel(time_inc)

	if printRow:
		printEdRow(time)
	return time_inc


def showPatmAndThrustAtAlts(minAlt, maxAlt, step):
	for altitude in range (minAlt, maxAlt+1, stepBy):
		patm  = percentOfAtmosphericPressure(altitude)
		pctVac = 1 - patm
		print ("{} : Perc ATM {}, OV {}".format(altitude, patm, orbitalVelocity(altitude)))
		for engine in HLV.engines:
			thrust_alt = engine.thrustAtAlt(altitude)
			print("{}: {}".format(engine.name, thrust_alt))


alt = 30.0
time = 0.0
endTime = 10.0
time_inc = 1.0




i = 1
table_data = []
def setInitialConditions():
	for i in range(2):
		# set each weight twice to set average weight
		HLV.setEngineThrottleOverride("RD-180", "max")
		HLV.setEngineThrottleOverride("SSME", "max")
		HLV.setEngineThrottleOverride("RD-171M", 0.56)
		HLV.setEngineThrottleOverride("SRM", 1)
		HLV.setEngineAssignedThrustPerEngine("SRM", "max")



def printEdRow(time):
	edRow(
		bigG(HLV.get_V_horiz_mph(), HLV.get_OrbitalV()),
		HLV.get_V_vert_inc(),
		time,
		HLV.get_currentWeight(),
		HLV.get_A_total(),
		HLV.get_V_horiz_mph(),
		HLV.get_airSpeed(),
		HLV.get_A_vert_eff(),
		HLV.get_A_horiz(),
		HLV.get_V_vert(),
		HLV.get_alt(),
		HLV.getTotalThrust(),
		HLV.get_ADC_predicted(),
		HLV.get_ADC_actual(),
		HLV.get_ADC_adjusted(),
		HLV.get_A_total_eff()

	)


def predict_ADC(rocket, time, time_inc, time_incs, events, assigned_V):
	threshold = 0.0000001
	ADC_error = 100000.0
	ADC_prediction = 0
	tries = 0
	while abs(ADC_error) > threshold:
		rocketCopy = copy.deepcopy(rocket)
		stopPrinting(lambda: compute_row(rocketCopy, time, time_inc, time_incs, events, ADC_prediction, assigned_V, False))
		ADC_error = rocketCopy.get_ADC_error()
		ADC_actual = rocketCopy.get_ADC_actual()
		#print ("Predicted ADC = {}\nerror={}\n=his prediction {}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, hisPredictedADC*10000.0, ADC_actual*10000.0))
		ADC_prediction -= ADC_error/2.0
		#print ("New Prediction = {}".format(ADC_prediction*10000.0))
		rocketCopy = None
		tries += 1
	return ADC_prediction

def initializeRocket():

	totalThrust = HLV.getTotalThrust()
	time = 0
	time_inc = 1.0

	HLV.updateA()
	HLV.updateVertA(HLV.get_A_total_eff())
	HLV.update_V_vert()
	HLV.update_ADC_actual(time_inc)
	HLV.setEngineThrottle("RD-171M", "max", time_inc)
	HLV.burnFuel(time_inc)
	printEdRow(time)
	#time_inc = float(raw_input("Enter the time inc:"))
	time_inc = 1.0
	time += time_inc

def simRocket():
	time = 1
	time_inc = 1.0



	asssigned_vs = ["a", "a", "a", "a", "a", 0.55, 0.563, 0.56, 0.55, 0.55, 0.55, 0.515, 0.518, 0.51, 0.489, 0.495, 0.494, 0.510, 0.534, 0.560,
		0.570, 0.58, 0.59, 0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52, 0.51, 0.5, 0.5, 0.5, 0.48, 0.46, 0.44, 0.42, 0.3, 0.3, 0.3,
		0.3, 0.3, 0.221111032, 0.0, 0.0, 0.0, 0.0, 0.0, -0.2, -0.22, -0.44, -0.42, -0.4, -0.38, -0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22
		-0.20, -0.18, -0.16, -0.16, -0.13, -0.10, 0.012808983, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.20, -0.25, -0.40, -0.38,
		-0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22, -0.20, -0.18, -0.16, -0.14, -0.12, -0.10, -0.10, -0.10, -0.10, -0.10
	]
	time_incs_json = load_json('time_incs.json')
	time_incs = time_incs_json['time_incs']

	events = [
		{
			"name" : "Increase Throttle By Max Rate-Of-Change",
			"engine": "RD-171M",
			"start_time": 0.00,
			"end_time" : 3.00,
		},
		{
			"name" : "Reduce Thrust",
			"engine": "SRM",
			"start_time": 24.00,
			"end_time" : 45.00,
			"rate" : -20000.0,
		},
		{
			"name" : "Reduce Thrust Until Depleted",
			"engine": "SRM",
			"start_time": 102.00,
			"end_time" : 114.00,
		},
		{
			"name" : "Jettison",
			"engine": "SRM",
			"start_time": 114.10,
			"end_time" : 114.10,
		},
		{
			"name" : "Reduce Throttle By Max Rate-Of-Change",
			"engine": "RD-171M",
			"start_time": 137.00,
			"end_time" : 140.00,
		},
		{
			"name" : "Engine Cut-off",
			"engine": "RD-171M",
			"start_time": 140.00,
			"end_time" : 140.00,

		}
	]
	i = 0
	while time <= 99:
		assigned_V = asssigned_vs[i]
		i += 1
		predictedADC = predict_ADC(HLV, time, time_inc, time_incs, events, assigned_V)
		time_inc = compute_row(HLV, time, time_inc, time_incs, events, predictedADC, assigned_V) #returns time_inc
		time += time_inc


setInitialConditions()
initializeRocket()
simRocket()
