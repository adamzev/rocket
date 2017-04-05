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
		"throt" : 1.0,
		"engine_count" : 4.0,
		"specImp_sl" : 242.00,
		"specImp_vac" : 268.20,
		"thrust_controlled" : True
	},
	{
		"name": "RD-171",
		"thrust_sl"  : 1632000.0,
		"thrust_vac" : 1777000.0,
		"throt" : 1.0,
		"engine_count" : 6.0,
		"specImp_sl" : 309.68,
		"specImp_vac" : 337.19
	},
	{
		"name": "RS-68A",
		"thrust_sl"  : 702000.0,
		"thrust_vac" : 797000.0,
		"throt" : 1.0,
		"engine_count" : 2.0,
		"burn_rate" : 1924.0#only need burn rate not specIn
	},
	{
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"throt" : 0.95,
		"engine_count" : 6.0,
		"burn_rate" : 1129.0
	},
	{
		"name": "RL-10A4-2",
		"thrust_sl"  : 22300.0,
		"thrust_vac" : 22300.0,
		"throt" : 0.95,
		"engine_count" : 1.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
	{
		"name": "OME",
		"thrust_sl"  : 6002.0,
		"thrust_vac" : 6002.0,
		"throt" : 0.95,
		"engine_count" : 2.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
	{
		"name": "GE90-115B",
		"thrust_sl"  : 115300.0,
		"thrust_vac" : 115300.0,
		"throt" : 0.95,
		"engine_count" : 3.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
]

data = {'rec1': {'col1': 99.88, 'col2': 108.79, 'label': 'rec1'},
'rec2': {'col1': 99.88, 'col2': 108.79, 'label': 'rec2'}
}


HLV = Vehicle("HLV * 4-6/2-6 MK: 3-30 Ver: 03-27-2017", 15674000, 1.204)

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


for engine in  HLV.engines:
	engine.setThrottle(0.95)

i = 1
table_data = []

headerRow = ["Time", "Alt"]

for key, value in HLV.V.iteritems():
	headerRow.append("V_" + str(key))
for key, value in HLV.A.iteritems():
	headerRow.append("A_" + str(key))

headerRow.append("Fuel Used")
headerRow.append("Thrust")
headerRow.append("W")
table_data.append(headerRow)

while (time <= endTime):
	row = []

	row.append(time)
	HLV.updatePrev() #sets all "prev" variables
	# GUESS AERO DRAG (see how much your previous guess was off, and sub or add)
	totalThrust = HLV.getTotalThrust()
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
	row.append("{:.1f}".format(HLV.alt))

	for key, value in HLV.V.iteritems():
		row.append("{:.1f}".format(value))
	for key, value in HLV.A.iteritems():
		row.append("{:.1f}".format(value))
	row.append("{:.1f}".format(fuelUsed))

	row.append("{:.1f}".format(totalThrust))
	row.append("{:.1f}".format(HLV.currentWeight))
	table_data.append(row)
	if time < 24:
		pass


	i +=1
	time += time_inc
printTable(table_data)

#showPatmAndThrustAtAlts(0, 30000, 1000)
