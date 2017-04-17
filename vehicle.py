from rocketEngine import *
from physics import Physics
from stage import *
from generalEquations import *
from util import *


class Vehicle(Physics):

	def __init__(self, specs, load_time_incs = False):
		self.name = "{} MK {} VER: {}".format(specs["name"], specs["MK"], specs["ver"])
		self.load_time_incs = load_time_incs
		self.stages = self.init_stages(specs["stages"])
		self.engines = []
		self.attach_engines(specs["engines"])
		self.set_engine_initial_fuel_source()
		self.lift_off_weight = specs["lift_off_weight"]
		self.set_adc_K(specs["stages"])
		self.currentWeight = self.lift_off_weight

		self.time = 0.0
		if load_time_incs:
			time_incs_json = load_json('time_incs.json')
			self.time_incs = time_incs_json['time_incs']
			self.set_time_inc()
		else:
			self.time_inc = 0.1
		self.alt = []
		self.alt.append(specs["initial_alt"])

		self.tower_height = specs["tower_height"]
		self.A_hv_diff = specs["A_hv_diff"]

		self.orbitalV = 0
		self.A_vert_eff = [0.0]
		self.A_vert = [0.0]
		self.A_horiz = [0.0]
		self.A_total = [0.0]
		self.A_total_eff = [0.0]
		self.V_vert = [0.0]
		self.V_vert_eff = [0.0]
		self.V_vert = [0.0]
		self.V_vert_inc = [0.0]
		self.V_horiz_mph =[912.67]
		self.V_horiz_mph_inc = [0.0]
		self.V_total = [0.0]
		self.total_eff = [0.0]
		self.ADC_adjusted = [0.0]
		self.ADC_error = [0.0]
		self.ADC_predicted = [0.0]
		self.ADC_actual = [0.0]
		self.orbitalV = orbitalVelocity(current(self.alt))


	def __str__(self):
		current_bigG = bigG(self.get_V_horiz_mph(), self.get_OrbitalV())
		totalA = self.get_A_total()
		V_horiz = self.get_V_horiz_mph()
		V_as = self.get_airSpeed()
		A_v =self.get_A_vert_eff()
		A_h = self.get_A_horiz()
		V_vert = self.get_V_vert()
		alt = self.get_alt()
		thrust = self.getTotalThrust()
		ADC_guess = self.get_ADC_predicted()
		ADC_adj = self.get_ADC_adjusted()

		row1 = "-"*140 + "\n"
		row2 = "{:>46.6f}      {:>6.8f}     G={: <12.8f}\n".format(self.get_A_total_eff(), self.get_ADC_actual(), current_bigG)
		time_string = "{:<6.1f}".format(self.time)
		time_string = Fore.RED + time_string + Style.RESET_ALL
		row3 = "+{:<12.2f} {:5} WT={:<11.2f}->{:>9.6f}      {:<12.8f}   Vh={:<12.6f} Vas={:<12.3f}     {:<12.6f}-{:<10.8f}\n".format(
			self.get_V_vert_inc(), time_string, self.get_currentWeight(), totalA, ADC_adj, V_horiz, V_as, A_v, A_h
		)
		alt_string = "ALT={:<.1f}\'".format(alt)
		row4 = "{:<13.6f} {:<16} T={:<19.4f}  \"{:<.4f}\"\n".format(V_vert, alt_string, thrust, ADC_guess)
		return row1+row2+row3+row4
	@staticmethod
	def load_available_engines():
		available_engines_json = load_json("rocketEngineData.json")
		return available_engines_json["rocketEngines"]

	@staticmethod
	def load_engine_data(selected_engines):
		available_engines  = Vehicle.load_available_engines()

		engine_data = []
		for selected_engine in selected_engines:
			name = selected_engine["engine_name"]
			count = selected_engine["engine_count"]
			try:
				engine = available_engines[name]
				engine["engine_count"] = count
				engine["name"] = name
				engine_data.append(engine)
			except:
				print ("ERROR Engine {} not found".format(name))
		return engine_data

	def set_time_inc(self):
		for timeIncrements in self.time_incs:
			if self.time < timeIncrements["until"]:
				self.time_inc = timeIncrements["time_inc"]
				break
	def tick(self):
		if self.load_time_incs:
			self.set_time_inc()
		self.time += self.time_inc

	def init_stages(self, stage_data):
		stages = {}
		for stage_type, stage_datum in stage_data.iteritems():
			stages[stage_type] = Stage(stage_datum)
		return stages

	def set_engine_initial_fuel_source(self):
		for engine in self.engines:
			if engine.type == "Solid":
				engine.set_fuel_source(self.stages["SRB"])
				self.stages["SRB"].fueling(engine)
			else:
				engine.set_fuel_source(self.stages["RLV"])
				self.stages["RLV"].fueling(engine)


	def attach_engine(self, engine_data):
		if engine_data["type"] == "Solid":
			engine = SolidRocketEngine(engine_data)
		elif engine_data["type"] == "Liquid":
			engine = LiquidRocketEngine(engine_data)
		else:
			raise ValueError("Unsupported engine type.")
		self.engines.append(engine)


	def attach_engines(self, selected_engines):
		''' loads engine data from file matching the given names
		'''
		engine_data = Vehicle.load_engine_data(selected_engines)
		for engine in engine_data:
			self.attach_engine(engine)

	def set_adc_K(self, stages):
		adc_K = 0.0
		for stage_name, stage_values in stages.iteritems():
			adc_K += stage_values["adc_K"]
		self.adc_K = adc_K


	def set_alt(self, alt):
		self.alt.append(alt)


	def get_alt(self, when = "current"):
		return get_value(self.alt, when)

	def get_V_horiz_mph(self, when = "current"):
		return get_value(self.V_horiz_mph, when)

	def get_V_vert_inc(self, when = "current"):
		return get_value(self.V_vert_inc, when)

	def get_V_horiz_mph_inc(self, when = "current"):
		return get_value(self.V_horiz_mph_inc, when)

	def get_V_vert(self, when = "current"):
		return get_value(self.V_vert, when)

	def get_OrbitalV(self):
		return self.orbitalV

	def get_A_total(self, when = "current"):
		return get_value(self.A_total, when)

	def get_A_total_eff(self, when = "current"):
		return get_value(self.A_total_eff, when)

	def get_A_horiz(self, when = "current"):
		return get_value(self.A_horiz, when)

	def get_A_vert(self, when = "current"):
		return get_value(self.A_vert, when)


	def get_A_vert_eff(self, when = "current"):
		return get_value(self.A_vert_eff, when)

	def get_currentWeight(self):
		return self.currentWeight

	def get_ADC_actual(self, when = "current"):
		return get_value(self.ADC_actual, when)

	def get_ADC_predicted(self, when = "current"):
		return get_value(self.ADC_predicted, when)

	def get_ADC_adjusted(self, when = "current"):
		return get_value(self.ADC_adjusted, when)

	def get_ADC_error(self, when = "current"):
		return get_value(self.ADC_error, when)

	def updateAlt (self, time_inc):
		self.alt.append(altitude(self.get_alt(), self.get_V_vert("prev"), self.get_V_vert_inc(), time_inc))

	def detachEngine(self, engineName):
		self.engines[:] = [d for d in self.engines if d.get('name') != engineName]

	def updateWeight(self, time_inc):
		fuel_used = 0.0
		fuel_burn = 0.0
		for name, stage in self.stages.iteritems():
			fuel_used += stage.fuel_used
		self.currentWeight = self.lift_off_weight - fuel_used

	def update_V(self, time_inc):
		self.update_V_vert_inc(time_inc)
		self.update_V_vert()
		self.update_V_horiz_mph_inc(time_inc)
		self.update_V_horiz_mph()


	def update_V_vert_inc(self, time_inc):
		avg_A_vert_eff = average(self.get_A_vert_eff(), self.get_A_vert_eff("prev"))
		self.V_vert_inc.append(avg_A_vert_eff * time_inc * ACCEL_OF_GRAVITY)

	def update_V_vert(self):
		self.V_vert.append(self.get_V_vert() + self.get_V_vert_inc())

	def update_V_horiz_mph_inc(self, time_inc):
		avg_A_horiz = average(self.get_A_horiz(), self.get_A_horiz("prev"))
		self.V_horiz_mph_inc.append(avg_A_horiz * time_inc * ACCEL_OF_GRAVITY)


	def update_V_horiz_mph(self):
		self.V_horiz_mph.append(self.get_V_horiz_mph() + fpsToMph(self.get_V_horiz_mph_inc()))



	def set_ADC_predicted(self, predictedADC):
		self.ADC_predicted.append(predictedADC)

	def select_A_vert(self):
		if self.get_alt() <= self.tower_height:
			return "a"
		orbitalV = orbitalVelocity(current(self.alt))
		A_horiz = A_vert_eff = 0.0
		A = self.get_A_total_eff()
		G = bigG(self.get_V_horiz_mph(), orbitalV)

		A_horiz_bump = 0.01
		while A_horiz <= A_vert_eff + self.A_hv_diff:
			A_horiz = ((math.sqrt(2.0*A**2.0 - G**2.0))-G)/2.0 + A_horiz_bump
			A_vert = pythag(None, A_horiz, A)
			A_vert_eff = A_vert - G
			A_horiz_bump += 0.01

		return A_vert_eff

	def updateA(self):
		totalA = self.getTotalThrust() / self.currentWeight
		self.A_total.append(totalA)
		self.ADC_adjusted.append(self.get_ADC_predicted() - self.get_ADC_error())
		self.A_total_eff.append(totalA - self.get_ADC_adjusted())
		#self.ADC_prediction_report(predictedADC, self.get_ADC_error())

	def update_ADC_actual(self, time_inc):
		self.ADC_actual.append(ADC(self.get_airSpeed(), self.get_alt(), self.adc_K))  # with resultant ADC in  "g" units
		self.ADC_error.append(self.get_ADC_predicted() - self.get_ADC_actual())

	def ADC_prediction_report(self, predictedADC, error):
		print ("Actual ADC={} predictedADC={} error={}".format(self.get_ADC_actual(), predictedADC, error))

	def updateVertA(self, assignedA_vert, calcG = True):
		orbitalV = orbitalVelocity(current(self.alt))
		G = bigG(self.get_V_horiz_mph(), orbitalV)
		self.orbitalV = orbitalVelocity(current(self.alt))


		if calcG:
			self.A_vert.append(assignedA_vert)
			self.A_vert_eff.append(assignedA_vert - G)
		else:
			self.A_vert.append(assignedA_vert + G)
			self.A_vert_eff.append(assignedA_vert)

	def updateHorizA(self):
		self.A_horiz.append(
			pythag(None, self.get_A_vert(), self.get_A_total_eff())
		)
		try:
			pass

		except:
			raise ValueError("Sqrt of negative, A total={} which is > A_vert={}".format(self.get_A_total_eff("prev"), self.get_A_vert()))


	def get_airSpeed(self, when = "current"):
		if when == "current":
			return pythag(fpsToMph(self.get_V_vert()), self.get_V_horiz_mph()-912.67)
		if when == "prev":
			return pythag(fpsToMph(self.get_V_vert("prev")), self.get_V_horiz_mph("prev")-912.67)


	def getTotalThrust(self):
		totalThrust = 0
		for engine in self.engines:
			totalThrust += engine.thrustAtAlt(self.get_alt())
		return totalThrust

	def burnFuel(self, time_inc):
		for engine in self.engines:
			 engine.burnFuel(time_inc, self.get_alt())

	def getTotalFuelUsed(self):
		fuelUsed = 0
		for name, stage in self.stages:
			fuelUsed += stage.fuelUsed
		return fuelUsed

	def setEngineThrottleOverride(self, engineName, throt):
		engine = self.find_engine(engineName)
		if throt == "max":
			engine.setThrottleOverride(engine.max_throt)
		elif throt == "min":
			engine.setThrottleOverride(engine.min_throt)
		elif throt == "off":
			engine.setThrottleOverride(0.0)
		else:
			engine.setThrottleOverride(throt)

	def setEngineThrottle(self, engineName, throt, time_inc):
		engine = self.find_engine(engineName)
		if throt == "max":
			engine.setThrottle(engine.max_throt, time_inc)
		else:
			engine.setThrottle(throt, time_inc)

	def setEngineAssignedThrustPerEngine(self, engineName, thrust):
		engine = self.find_engine(engineName)
		if thrust == "max":
			engine.set_assigned_thrust_per_engine(engine.thrust_sl)
		else:
			engine.set_assigned_thrust_per_engine(thrust)


	def get_engine_throttle(self, engineName):
		engine = self.find_engine(engineName)
		return engine.throt

	def find_engine(self, engineName):
		for engine in self.engines:
			if engine.name == engineName:
				return engine

	def engine_status(self, engineName = None):
		if engineName:
			engines = [self.find_engine(engineName)]
		else:
			engines = self.engines
		for engine in engines:
			print "Name: {}\nThrottle: {}\nThrust: {}\nFuel Used: {}".format(engine.name, engine.get_throt(),engine.get_thrust_total(), engine.get_fuelUsed())


	def handle_stage_event(self, event):
		stage = self.stages[event["stage"]]
		start_time = event["start_time"]
		end_time = event["end_time"]

		if event["name"] == "Jettison":
			stage.jettison()
			self.adc_K -= stage.adc_K
			for engine in self.engines:
				if engine.stage == stage.type:
					engine.setThrottleOverride(0)
					engine.setThrottleOverride(0)
				if engine.stage == "orbiter" and stage.type == "RLV":
					#orbiter engines use RLV as fuel source until RLV is jettisoned
					engine.set_fuel_source(self.stages["orbiter"])

	def handle_engine_event(self, event):
		engine = self.find_engine(event["engine"])
		start_time = event["start_time"]
		end_time = event["end_time"]

		if event["name"] == "Reduce Thrust" and self.time < event["end_time"]:
			engine.reduceThrust(event["rate"], self.time_inc)

		if event["name"] == "Power Down":
			engine.power_down(start_time, end_time, self.time, self.time_inc, self.get_alt())


		if event["name"] == "Increase Throttle By Max Rate-Of-Change":
			engine.setThrottle(engine.max_throt, self.time_inc)

		if event["name"] == "Reduce Throttle By Max Rate-Of-Change":
			engine.setThrottle(engine.min_throt, self.time_inc)

		if event["name"] == "Engine Cut-off":
			engine.setThrottleOverride(0.0)
			engine.setThrottleOverride(0.0)
			print("\nEVENT: {} cut-off".format(engine.name))
