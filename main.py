import math
import logging
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
		"thrust_controlled" : True
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
	predictedADC = 0.00012
	HLV.set_ADC_predicted(0.00012)
	printEdRow(time)
	#time_inc = float(raw_input("Enter the time inc:"))
	time_inc = 1.0
	time += time_inc

def simRocket():
	time = 1
	time_inc = 1.0

	predictedADCs = [0.00086, 0.0022, 0.0043, 0.01106, 0.0268, 0.0448, 0.077, 0.127, 0.171, 0.2148, 0.2798, 0.3239, 0.3615, 0.4135, 0.4497, 0.487,
		0.5109, 0.5284, 0.5370, 0.5540, 0.5533, 0.555, 0.5515, 0.5376, 0.5222, 0.5016, 0.4678, 0.4739, 0.4359, 0.4089, 0.3864, 0.356, 0.3248, 0.2945,
		0.2725, 0.239, 0.211, 0.184, 0.156, 0.131, 0.131, 0.0932, 0.0793, 0.06756, 0.0587
	]

	asssigned_vs = ["a", "a", "a", "a", "a", 0.55, 0.563, 0.56, 0.55, 0.55, 0.55, 0.515, 0.518, 0.51, 0.489, 0.495, 0.494, 0.510, 0.534, 0.560,
		0.570, 0.58, 0.59, 0.6, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52, 0.51, 0.5, 0.5, 0.5, 0.48, 0.46, 0.44, 0.42, 0.3, 0.3, 0.3,
		0.3, 0.3, 0.221111032, 0, 0, 0, 0, 0, -0.2, -0.22, -0.44, -0.42, -0.4, -0.38, -0.36, -0.34, -0.32, -0.30, -0.28, -0.26, -0.24, -0.22
		-0.20, -0.18, -0.16
	]
	time_incs = [
		{
			"time_inc" : 1.0,
			"until" : 4.0
		},
		{
			"time_inc" : 2.0,
			"until" : 6.0
		},
		{
			"time_inc" : 3.0,
			"until" : 114.0
		},
		{
			"time_inc" : 0.1,
			"until" : 114.1
		},
		{
			"time_inc" : 2.9,
			"until" : 117.0
		},
		{
			"time_inc" : 3.0,
			"until" : 135.0
		},
		{
			"time_inc" : 2.0,
			"until" : 137.0
		},
		{
			"time_inc" : 1.0,
			"until" : 140.0
		},
		{
			"time_inc" : 0.1,
			"until" : 140.1
		},
		{
			"time_inc" : 0.9,
			"until" : 141.0
		},
		{
			"time_inc" : 0.9,
			"until" : 141.0
		}
	]

	events = [
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
			"name" : "Reduce Throttle",
			"engine": "RD-171M",
			"start_time": 137.00,
			"end_time" : 140.00,
		},
	]

	for i in range(len(predictedADCs)):
		for event in events:
			if time >= event["start_time"] and time <= event["end_time"]:
				HLV.handle_event(event, time, time_inc)
		predictedADC = predictedADCs[i]
		assigned_V = asssigned_vs[i]
		#HLV.engine_status()
		HLV.setEngineThrottle("RD-171M", "max", time_inc)
		HLV.updateWeight(time_inc)
		HLV.updateA()
		#assigned_V = raw_input("Enter the assigned A_vert:")


		if assigned_V == "a" or assigned_V == "all":
			assigned_V = HLV.get_A_total_eff()
			HLV.updateVertA(assigned_V)
		else:
			assigned_V = float(assigned_V)
			HLV.updateVertA(assigned_V, False)



		HLV.updateHorizA()
		HLV.update_V(time_inc)
		HLV.updateAlt(time_inc)
		HLV.update_ADC_actual(time_inc)
		for timeIncrements in time_incs:
			if time<timeIncrements["until"]:
				time_inc = timeIncrements["time_inc"]
				break
		HLV.burnFuel(time_inc)
		HLV.set_ADC_predicted(predictedADC)
		printEdRow(time)


		time += time_inc


setInitialConditions()
initializeRocket()
simRocket()

'''
def predict_ADC(self):
	rocketCopy = copy.deepcopy(HLV)
	threshold = 0.000001
	ADC_error = 100000
	while ADC_error>threshold:
		guess an adc of 0
		calculate a row
		find error
		repeat and guess an adc of prior guess + error
		guess 0, drag is .4, guess .4, drag is .2 guess .2 drag is .3 and so on
'''
