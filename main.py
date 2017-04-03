import math
from rocketEngine import *
from vehicle import *
from generalEquations import *




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

HLV = Vehicle("HLV * 4-6/2-6 MK: 3-30 Ver: 03-27-2017", 15674000, 1.204)

for engine in engineData:
	HLV.attachEngine(engine)



for altitude in range (0, 30000, 1000):
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
while (time <= endTime):
	HLV.updatePrev() #sets all "prev" variables
	HLV.updateAlt(time_inc)
	HLV.updateIncVertV()
	HLV.updateVertA()
	HLV.updateVertV(time_inc)
	HLV.updateHorizA()


	# ***************THRUST*****************
	totalThrust = 0
	for engine in  HLV.engines:
		thrust_alt = engine.thrustAtAlt(alt)
		totalThrust += thrust_alt
	# up to Solid Rocket Booster Thrust (TSRB)

	HLV.getAirSpeed()

	K = HLV.adc_K
	ADC = ((HLV.getAirSpeed() / 1000.0)**2) * patm * K # with resultant ADC in  "g" units
	HLV.updateWeight(time_inc)
	totalWeight = HLV.currentWeight
	totalA = totalThrust / totalWeight

	# A = pythag(horizA, vertA)
	A = totalA - ADC
	'''   *** How much of the A is vert and how much is horiz? Right now assuming all vert '''
	vertA = A
	horizA = 0


	print ("Time {} :Alt {}".format(time, HLV.alt))
	if time < 24:
		pass



	time += time_inc
