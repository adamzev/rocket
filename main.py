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
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
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
		HLV.setEngineAssignedThrust("SRM", "max")



def printEdRow(time, totalThrust):
	edRow(
		bigG(HLV.get_V_horiz(), HLV.get_OrbitalV()),
		HLV.get_V_vert_inc(),
		time,
		HLV.get_currentWeight(),
		HLV.get_A_total(),
		HLV.get_A_horiz(),
		HLV.get_airSpeed(),
		HLV.get_A_vert_eff(),
		HLV.get_A_horiz(),
		HLV.get_V_vert(),
		HLV.get_alt(),
		totalThrust)


def initializeRocket():

	totalThrust = HLV.getTotalThrust()
	time = 0
	time_inc = 1.0
	predictedADC = 0.0
	HLV.updateA(predictedADC)
	HLV.updateVertA(HLV.get_A_total_eff())
	HLV.updateVertV()
	HLV.setEngineThrottle("RD-171M", "max", time_inc)
	HLV.burnFuel(time_inc)
	printEdRow(time, totalThrust)
	#time_inc = float(raw_input("Enter the time inc:"))
	time_inc = 1.0
	time += time_inc

def simRocket():
	time = 1
	time_inc = 1.0

	predictedADCs = [0.00012, 0.00086, 0.0022, 0.0043, 0.01106, 0.0268, 0.0448, 0.0777, 0.127, 0.171, 0.2148, 0.2798, 0.3239, 0.3615, 0.4135, 0.4147, 0.487,
		0.5109, 0.5284, 0.5370, 0.5540, 0.5533, 0.555, 0.5515, 0.5376, 0.5222, 0.5016, 0.4678, 0.4739, 0.4359, 0.4089, 0.3864, 0.356, 0.3248, 0.2945]
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
		}
	]
	for predictedADC in predictedADCs:

		totalThrust = HLV.getTotalThrust()
		#HLV.engine_status()
		HLV.setEngineThrottle("RD-171M", "max", time_inc)
		HLV.updateWeight(time_inc)
		HLV.updateA(predictedADC)
		assigned_V = raw_input("Enter the assigned A_vert:")
		if assigned_V == "a" or assigned_V == "all":
			assigned_V = HLV.get_A_total_eff()
			HLV.updateVertA(assigned_V)
		else:
			assigned_V = float(assigned_V)
			HLV.updateVertA(assigned_V, False)



		HLV.updateHorizA()
		HLV.updateIncVertV(time_inc)
		HLV.updateVertV()
		HLV.updateAlt(time_inc)
		for timeIncrements in time_incs:
			if time<timeIncrements["until"]:
				time_inc = timeIncrements["time_inc"]
				break
		HLV.burnFuel(time_inc)
		printEdRow(time, totalThrust)


		time += time_inc


setInitialConditions()
initializeRocket()
simRocket()
