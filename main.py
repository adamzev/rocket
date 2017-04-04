import math
import logging
from rocketEngine import *
from vehicle import *
from generalEquations import *
from util import *
log = logging.basicConfig(level=logging.INFO)

engineData = [
	{
		"name": "RD-171",
		"thrust_sl"  : 1632000.0,
		"thrust_vac" : 1777000.0,
		"throt" : 1.0,
		"engine_count" : 1.0,
		"specImp_sl" : 309.68,
		"specImp_vac" : 337.19
	},
	{
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"throt" : 0.95,
		"engine_count" : 1.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	},
	{
		"name": "SRB",
		"thrust_sl"  : 3600000.0,
		"thrust_vac" : 3600000.0,
		"throt" : 1.0,
		"engine_count" : 1.0,
		"specImp_sl" : 242.00,
		"specImp_vac" : 268.20
	}
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

def hello():
    return "Hello, World!"




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

	HLV.updateIncVertV()
	HLV.updateVertA()
	HLV.updateVertV(time_inc)


	# ***************THRUST*****************
	totalThrust = 0

	totalThrust = HLV.getTotalThrust()
	HLV.burnFuel(time_inc)
	fuelUsed = HLV.getTotalFuelUsed()


	HLV.getAirSpeed()

	K = HLV.adc_K
	ADC = ((HLV.getAirSpeed() / 1000.0)**2) * percentOfAtmosphericPressure(alt) * K # with resultant ADC in  "g" units
	HLV.updateWeight(time_inc)
	totalWeight = HLV.currentWeight
	totalA = totalThrust / totalWeight

	# A = pythag(horizA, vertA)
	A = totalA - ADC
	print A
	''' MOVE TO CLASS '''
	if A > 0.6 + bigG(HLV.V['horiz'], HLV.orbitalV):
		HLV.A["vert"] = vertA = 0.6 + bigG(HLV.V['horiz'], HLV.orbitalV)
	else:
		HLV.A["vert"] = A
	HLV.A["horiz"] = math.sqrt(A**2 - HLV.A["vert"]**2)

	HLV.updateAlt(time_inc)
	row.append("{:.1f}".format(HLV.alt))

	for key, value in HLV.V.iteritems():
		row.append("{:.1f}".format(value))
	for key, value in HLV.A.iteritems():
		row.append("{:.1f}".format(value))
	row.append("{:.1f}".format(fuelUsed))

	row.append("{:.1f}".format(totalThrust))
	row.append("{:.1f}".format(totalWeight))
	table_data.append(row)
	if time < 24:
		pass


	i +=1
	time += time_inc
printTable(table_data)

#showPatmAndThrustAtAlts(0, 30000, 1000)
