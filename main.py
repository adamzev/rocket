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
		"burn_rate" : 14876.0325,
		"thrust_controlled" : True
	},
	{
		"name": "RD-171M",
		"thrust_sl"  : 1632000.0,
		"thrust_vac" : 1777000.0,
		"min_throt" : 0.56,
		"max_throt" : 1.0,
		"engine_count" : 8.0,
		"burn_rate" : 5270.0,
	},
	{
		"name": "RD-180",
		"thrust_sl"  : 861270.0,
		"thrust_vac" : 934245.0,
		"min_throt" : 0.40,
		"max_throt" : 0.95,
		"engine_count" : 6.0,
		"burn_rate" : 2770.0
	},
	{
		"name": "GE90-115B",
		"thrust_sl"  : 115300.0,
		"thrust_vac" : 115300.0,
		"max_throt" : 0.95,
		"engine_count" : 3.0,
		"burn_rate" : 8.0069444,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
	{
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"min_throt" : 0.40,
		"max_throt" : 0.95,
		"engine_count" : 9.0,
		"burn_rate" : 1129.0
	},
	{
		"name": "RL-10A4-2",
		"thrust_sl"  : 22300.0,
		"thrust_vac" : 22300.0,
		"max_throt" : 0.95,
		"engine_count" : 3.0,
		"burn_rate" : 49.4457
	},
	{
		"name": "OME",
		"thrust_sl"  : 6002.0,
		"thrust_vac" : 6002.0,
		"max_throt" : 0.95,
		"engine_count" : 3.0,
		"burn_rate" : 18.993671,
	},

]


HLV = Vehicle("HLV * 4-8/6-9 MK: 3-36 Ver: 08-12-2016", 22191271.27, 1.204)

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
		HLV.setEngineThrottle("RD-180", "max")
		HLV.setEngineThrottle("SSME", "max")
		HLV.setEngineThrottle("RD-171M", 0.56)
		HLV.setEngineThrottle("SRM", "max")



def thrustWeightAccelLoop():

	time = -1
	totalThrust = HLV.getTotalThrust()
	edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, HLV.alt, totalThrust)
	time = 0
	while True:
		time_inc = float(raw_input("Enter the time inc:"))
		throt = float(raw_input("Enter the RD-171 throt:"))

		HLV.setEngineThrottle("RD-171M", throt)
		#HLV.alt = float(raw_input("Enter the alt:"))
		totalThrust = HLV.getTotalThrust()

		edRow(big_G, HLV.V['vert_inc'], time,HLV.currentWeight, HLV.A['total'], HLV.V['horiz'], V_as, HLV.A['vert_eff'], HLV.A['horiz'], HLV.V['vert'], HLV.alt, totalThrust)
		HLV.burnFuel(time_inc)
		#fuelUsed = HLV.getTotalFuelUsed()
		HLV.updateWeight(time_inc)
		HLV.updateA()
		HLV.updateVertA(HLV.A['total'])
		HLV.updateHorizA()
		HLV.updateIncVertV()
		HLV.updateVertV(time_inc)

		HLV.updateAlt(time_inc)

		time += time_inc

V_vert= alt = big_G = V_vert_inc=  time = totalWeight = totalA = V_horiz =  V_as = A_v= A_h = 0.0
setInitialConditions()
thrustWeightAccelLoop()
row = []


totalThrust = HLV.getTotalThrust()

row.append("ALT = {:.1f}".format(HLV.alt))
row.append("T: {:.5f}".format(totalThrust))
table_data.append(row)




def mainSimLoop(endTime):
	while (time <= endTime):

		row = []


		HLV.updatePrev() #sets all "prev" variables
		# GUESS AERO DRAG (see how much your previous guess was off, and sub or add)
		HLV.alt = 50
		totalThrust = HLV.getTotalThrust()

		row.append(time)
		HLV.burnFuel(time_inc)
		fuelUsed = HLV.getTotalFuelUsed()

	#	HLV.getAirSpeed()

		HLV.updateWeight(time_inc)
		HLV.updateA()
		HLV.updateVertA()
		HLV.updateHorizA()
		HLV.updateIncVertV()
		HLV.updateVertV(time_inc)

		HLV.updateAlt(time_inc)


		'''for key, value in HLV.V.iteritems():
			row.append("{:.1f}".format(value))
		for key, value in HLV.A.iteritems():
			row.append("{:.1f}".format(value))
		row.append("{:.1f}".format(fuelUsed))
		'''
		row.append("ALT = {:.1f}".format(HLV.alt))
		row.append("T: {:.5f}".format(totalThrust))
		table_data.append(row)

		printTable(table_data, 8)
		table_data = []

		time_inc = float(raw_input("Enter the time inc:"))
		prev_throt = HLV.getEngineThrottle("RD-171M")
		throt = float(raw_input("Enter the RD-171 throt:"))
		throt_avg = average(prev_throt, throt)
		HLV.setEngineThrottle("RD-171M", throt_avg)
		#ADC_guess = float(raw_input("Guess drag:"))
		#vertA = float(raw_input("Assign vertA:"))
		row = []

		i +=1
		time += time_inc
#printTable(table_data, 8)

#showPatmAndThrustAtAlts(0, 30000, 1000)
