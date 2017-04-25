from rocketEngine import *
from physicalStatus import PhysicalStatus
from stage import *
from generalEquations import *
from util import *
import copy


class Vehicle():

	def __init__(self, specs, load_time_incs = False):
		earth_rotation_mph = specs["earth_rotation_mph"]
		self.cur = PhysicalStatus(
			alt = specs["initial_alt"],
			earth_rotation_mph = earth_rotation_mph
		)
		self.cur.V.horiz_mph = earth_rotation_mph
		self.cur.V.vert = 0.0
		self.ground_level = specs["initial_alt"],
		self.cur.A.horiz = 0.0
		self.cur.A.vert = 0.0
		self.lift_off_weight = specs["lift_off_weight"]
		self.cur.weight = self.lift_off_weight
		self.prev = copy.deepcopy(self.cur)
		self.name = "{} MK {} VER: {}".format(specs["name"], specs["MK"], specs["ver"])
		self.load_time_incs = load_time_incs
		self.stages = self.init_stages(specs["stages"])
		self.engines = []
		self.attach_engines(specs["engines"])
		self.set_engine_initial_fuel_source()

		self.set_adc_K(specs["stages"])


		self.time = 0.0
		if load_time_incs:
			time_incs_json = load_json('time_incs.json')
			self.time_incs = time_incs_json['time_incs']
			self.set_time_inc()
		else:
			self.time_inc = 0.1

		self.tower_height = specs["tower_height"]
		self.A_hv_diff = specs["A_hv_diff"]


	def __str__(self):
		V_as = self.cur.V.air_speed_mph
		A_v = self.cur.A_vert_eff
		A_h = self.cur.A.horiz
		V_vert = self.cur.V.vert
		alt = self.cur.alt
		thrust = self.cur.force
		big_G = self.cur.big_G
		ADC_guess = self.cur.ADC_predicted
		ADC_adj = self.cur.ADC_adjusted
		sign_symb = "+" if self.cur.V.vert_inc>0 else "-"
		row1 = "-"*140 + "\n"
		row2 = "{:>46.6f}      {:>6.8f}     G={: <12.8f}\n".format(self.cur.A.total, self.cur.ADC_actual, big_G)
		time_string = "{:<6.1f}".format(self.time)
		time_string = Fore.RED + time_string + Style.RESET_ALL
		row3 = "{}{:<12.2f} {:5} WT={:<11.2f}->{:>9.6f}      {:<12.8f}   Vh={:<12.6f} Vas={:<12.3f}     {:<12.6f} {:<10.8f}\n".format(
			sign_symb, self.cur.V.vert_inc, time_string, self.cur.weight, self.cur.A.raw, ADC_adj, self.cur.V.horiz_mph, V_as, A_v, A_h
		)
		alt_string = "ALT={:<.1f}\'".format(alt)
		row4 = "{:<13.6f} {:<16} T={:<19.4f}  \"{:<.4f}\"\n".format(V_vert, alt_string, thrust, ADC_guess)
		return row1+row2+row3+row4
	def save_current_row(self, first = False):

		V_as = self.cur.V.air_speed_mph
		A_v = self.cur.A_vert_eff
		A_h = self.cur.A.horiz
		V_vert = self.cur.V.vert
		alt = self.cur.alt
		thrust = self.cur.force
		big_G = self.cur.big_G
		ADC_guess = self.cur.ADC_predicted
		ADC_adj = self.cur.ADC_adjusted
		ADC_error = self.cur.ADC_error
		row1 = "{:.1f}, {:.0f}, {:.4f}, {:.4f}, {:.9f}, {:.8f}, {:.6f}, {:.7f}, {:.7f}, {:.7f}, ".format(
			self.time,
			alt,
			thrust,
			self.cur.weight,
			ADC_guess,
			self.cur.ADC_actual,
			ADC_adj,
			ADC_error,
			self.cur.A.raw,
			self.cur.A.total
		)
		row2 = "{:.8f}, {:.5f}, {:.10f}, {:.6f}, {:.6f}, {:.1f}, {:.8f}\n".format(
			A_h,
			A_v,
			big_G,
			V_as,
			self.cur.V.horiz_mph,
			self.cur.V.vert_inc,
			V_vert


		)
		headers = "time, alt, thrust, weight, ADC_guess, ADC_actual, ADC_adj, ADC_error, A_raw, A_total, A_h, A_v, bigG, V_as, V_horiz_mph, V_vert_inc, V_vert \n"
		if first:
			create_csv(headers, 'data/rows.csv')
		save_csv(row1+row2, 'data/rows.csv')

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

	def get_time_inc(self):
		for timeIncrements in self.time_incs:
			if self.time  < timeIncrements["until"]:
				return timeIncrements["time_inc"]

	def get_A_vert_eff_avg(self):
		A_vert_eff = average(self.cur.A.vert_eff, self.prev.A.vert_eff)
		if self.cur.alt > self.ground_level:
			return A_vert_eff
		else:
			if A_vert_eff < 0:  #Not enough force to lift off, but don't move down if on the ground
				return 0.0
			else:
				return A_vert_eff #enough force to lift off

	def tick(self):
		if self.load_time_incs:
			self.set_time_inc()
		self.time += self.time_inc
		self.prev = copy.deepcopy(self.cur)
		self.cur = PhysicalStatus()


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


	def updateAlt (self, time_inc):
		self.cur.alt = altitude(self.prev.alt, self.prev.V.vert, self.cur.V.vert_inc, time_inc)

	def detachEngine(self, engineName):
		self.engines[:] = [d for d in self.engines if d.get('name') != engineName]

	def updateWeight(self, time_inc):
		fuel_used = 0.0
		fuel_burn = 0.0
		for name, stage in self.stages.iteritems():
			fuel_used += stage.fuel_used
		self.cur.weight = self.lift_off_weight - fuel_used

	def update_V_inc(self, time_inc):
		#self.update_V_horiz_mph()
		self.update_V_vert_inc(time_inc)
		self.update_V_horiz_mph_inc(time_inc)


	def update_V_vert_inc(self, time_inc):
		self.cur.V.vert_inc = self.get_A_vert_eff_avg() * time_inc * ACCEL_OF_GRAVITY

	def update_V_vert(self):
		self.cur.V.vert = self.prev.V.vert + self.cur.V.vert_inc #current or prev v inc?

	def update_V_horiz_mph_inc(self, time_inc):
		avg_A_horiz = average(self.cur.A.horiz, self.prev.A.horiz)
		self.cur.V.horiz_inc = avg_A_horiz * time_inc * ACCEL_OF_GRAVITY


	def update_V_horiz_mph(self):
		self.cur.V.horiz_mph = self.prev.V.horiz_mph + self.prev.V.horiz_mph_inc


	def select_A_vert(self):
		if self.cur.alt <= self.tower_height:
			return "a"
		A_horiz = A_vert_eff = 0.0
		A = self.cur.A.total
		G = self.cur.big_G

		A_horiz_bump = 0.01
		while A_horiz <= A_vert_eff + self.A_hv_diff:
			A_horiz = ((math.sqrt(2.0*A**2.0 - G**2.0))-G)/2.0 + A_horiz_bump
			A_vert = pythag(None, A_horiz, A)
			A_vert_eff = A_vert - G
			A_horiz_bump += 0.01

		return A_vert_eff

	def updateA(self):
		self.cur.A.set_raw(self.prev.force, self.cur.weight)
		self.cur.ADC_adjusted = self.prev.ADC_predicted - self.prev.ADC_error
		self.cur.A.total = self.cur.A.raw - self.cur.ADC_adjusted


	def update_ADC_actual(self, time_inc):
		self.cur.ADC_actual = ADC(self.cur.V.air_speed_mph, self.cur.alt, self.adc_K)  # with resultant ADC in  "g" units
		#self.ADC_prediction_report()
		self.cur.ADC_error = self.prev.ADC_predicted - self.cur.ADC_actual

	def ADC_prediction_report(self):
		print ("Actual ADC={} prev predictedADC={} cur predictedADC = {} error={}".format(self.cur.ADC_actual, self.prev.ADC_predicted, self.cur.ADC_predicted, self.cur.ADC_error))


	def get_total_thrust(self):
		totalThrust = 0
		for engine in self.engines:
			thrust = engine.thrustAtAlt(self.cur.alt)
			totalThrust += thrust
		return totalThrust

	def burnFuel(self, time_inc):
		for engine in self.engines:
			engine.burnFuel(time_inc, self.prev.alt)

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

	def display_engine_messages(self):
		for engine in self.engines:
			for message in engine.messages:
				print (message)
			engine.messages = []


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
		time_inc = self.get_time_inc()

		if event["name"] == "Reduce Thrust" and self.time < event["end_time"]:
			engine.reduceThrust(event["rate"], time_inc)

		if event["name"] == "Power Down":
			engine.power_down(start_time, end_time, self.time, time_inc, self.cur.alt)


		if event["name"] == "Increase Throttle By Max Rate-Of-Change":
			engine.setThrottle(engine.max_throt, time_inc)

		if event["name"] == "Reduce Throttle By Max Rate-Of-Change":
			engine.setThrottle(engine.min_throt, time_inc)

		if event["name"] == "Engine Cut-off":
			engine.setThrottleOverride(0.0)
			engine.setThrottleOverride(0.0)
			print("\nEVENT: {} cut-off".format(engine.name))
