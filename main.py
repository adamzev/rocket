import math
import logging
import copy

from rocketEngine import *
from vehicle import *
from generalEquations import *
from util import *
log = logging.basicConfig(level=logging.INFO)

engineData = [
	{
		"name": "SRM",
		"thrust_sl"  : 3600000.0,
		"thrust_vac" : 3600000.0,
		"min_throt" : 0.56,
		"max_throt" : 1.0,
		"engine_count" : 4.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"weight_fueled" : 6320000,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 1.0,
		"burn_rate" : [14876.0325],
		"assigned_thrust" : 0.0,
		"specImp_sl" : 242.00,
		"specImp_vac" : 268.20,
		"thrust_controlled" : True,
		"adc_K" : 0.28400
	},
	{
		"name": "RD-171M",
		"thrust_sl"  : 1632000.0,
		"thrust_vac" : 1777000.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"min_throt" : 0.56,
		"max_throt" : 1.0,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"engine_count" : 8.0,
		"burn_rate" : [5270.0],
	},
	{
		"name": "RD-180",
		"thrust_sl"  : 861270.0,
		"thrust_vac" : 934245.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"min_throt" : 0.40,
		"max_throt" : 0.95,
		"engine_count" : 6.0,
		"burn_rate" : [2770.0],
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
	},
	{
		"name": "GE90-115B",
		"thrust_sl"  : 115300.0,
		"thrust_vac" : 115300.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"max_throt" : 0.95,
		"engine_count" : 3.0,
		"burn_rate" : [8.0069444],
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
	{
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"min_throt" : 0.40,
		"max_throt" : 0.95,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"engine_count" : 9.0,
		"burn_rate" : [1129.0]
	},
	{
		"name": "RL-10A4-2",
		"thrust_sl"  : 22300.0,
		"thrust_vac" : 22300.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"max_throt" : 0.95,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"engine_count" : 3.0,
		"burn_rate" : [49.4457]
	},
	{
		"name": "OME",
		"thrust_sl"  : 6002.0,
		"thrust_vac" : 6002.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"max_throt" : 0.95,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"engine_count" : 3.0,
		"burn_rate" : [18.993671],
	},

]


HLV = Vehicle("HLV * 4-8/6-9 MK: 3-36 Ver: 08-12-2016", 22191271.27, 1.832)

for engine in engineData:
	HLV.attachEngine(engine)

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


alt = 0.0
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
	ADC_prediction = 0.0
	while abs(ADC_error) > threshold:
		rocketCopy = copy.deepcopy(rocket)
		stopPrinting(lambda: compute_row(rocketCopy, time, time_inc, time_incs, events, ADC_prediction, assigned_V, False))
		ADC_error = rocketCopy.get_ADC_error()
		ADC_actual = rocketCopy.get_ADC_actual()
		#print ("Predicted ADC = {}\nerror={}\n=his prediction {}\nadc_calc={}".format(ADC_prediction*10000.0, ADC_error*10000.0, hisPredictedADC*10000.0, ADC_actual*10000.0))
		ADC_prediction -= ADC_error/2.0
		#print ("New Prediction = {}".format(ADC_prediction*10000.0))
		rocketCopy = None
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
	for i in range(len(asssigned_vs)):
		assigned_V = asssigned_vs[i]
		predictedADC = predict_ADC(HLV, time, time_inc, time_incs, events, assigned_V)
		time_inc = compute_row(HLV, time, time_inc, time_incs, events, predictedADC, assigned_V) #returns time_inc
		time += time_inc


setInitialConditions()
initializeRocket()
simRocket()
