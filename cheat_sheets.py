def showPatmAndThrustAtAlts(engines, minAlt, maxAlt, step):
	for altitude in range (minAlt, maxAlt+1, stepBy):
		patm  = percentOfAtmosphericPressure(altitude)
		pctVac = 1 - patm
		print ("{} : Perc ATM {}, OV {}".format(altitude, patm, orbitalVelocity(altitude)))
		for engine in engines:
			thrust_alt = engine.thrustAtAlt(altitude)
			print("{}: {}".format(engine.name, thrust_alt))
