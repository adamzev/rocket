from math import sqrt
import copy

from colorama import Fore, Style

from physicalStatus import PhysicalStatus
import generalEquations as equ

from libs import fileManager as fileMan

import util.func as func
import mode

class Vehicle(object):

	def __init__(self, specs, stages, engines):
		earth_rotation_mph = specs["earth_rotation_mph"]
		self.cur = PhysicalStatus(
			alt=0,
			earth_rotation_mph=earth_rotation_mph
		)

		self.specs = specs
		self.time_incs = {}
		self.time_inc = 0.1
		self.stages = stages
		self.engines = engines
		self.load_time_incs = False
		self.V_v_target_hit = False # Has the rocket hit the V_v target
		self.V_v_start_giveback = False
		self.V_v_giveback_target_hit = False # Has the rocket hit the V_v giveback target
		self.A_v_giveback = -0.4
		self.V_v_target = 0.0
		self.V_v_giveback_target = 0.0
		self.time = 0
		self.cur.V.horiz_mph = earth_rotation_mph
		self.A_ease_in = 0.1 # used to adjust the acceleration to ease in to the target V_v
		self.A_ease_in_giveback = 0.1
		self.cur.V.vert = 0.0
		self.tower_height = 0
		self.ground_level = 0.0 # overwriten by initial alt
		self.adc_K = 0.0
		self.cur.A.horiz = 0.0
		self.cur.A.vert = 0.0
		self.V_v_accuracy = 0.0000001
		self.A_hv_diff = 0.0
		self.lift_off_weight = specs["lift_off_weight"]
		self.cur.weight = self.lift_off_weight
		self.prev = copy.deepcopy(self.cur)
		self.name = "{} MK {}".format(specs["name"], specs["MK"])


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
		sign_symb = "+" if self.cur.V.vert_inc > 0 else "-"
		row1 = "-"*140 + "\n"
		row2 = "{:>48,.6f}      {:>6,.8f}     G={: <12,.8f}\n".format(self.cur.A.total, self.cur.ADC_actual, big_G)
		time_string = "{:<6,.1f}".format(self.time)
		time_string = Fore.RED + time_string + Style.RESET_ALL
		row3 = "{}{:<12,.2f} {:5} WT={:<13,.2f}->{:>9,.6f}      {:<12,.8f}   Vh={:<12,.6f} Vas={:<12,.3f}     {:<12,.6f} {:<10,.8f}\n".format(
			sign_symb, self.cur.V.vert_inc, time_string, self.cur.weight, self.cur.A.raw, ADC_adj, self.cur.V.horiz_mph, V_as, A_v, A_h
		)
		alt_string = "ALT={:<,.1f}\'".format(alt)
		row4 = "{:<13,.6f} {:<16} T={:<19,.4f}  \"{:<,.4f}\"\n".format(V_vert, alt_string, thrust, ADC_guess)
		return row1+row2+row3+row4

	def save_current_row(self, first=False):
		''' Saves the current row to a csv file '''
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
			fileMan.create_csv(headers, 'data/rows.csv')
		fileMan.update_csv(row1+row2, 'data/rows.csv')



	def set_time_inc(self):
		''' sets the current time increment based on the current time and the time_incs object '''
		for timeIncrements in self.time_incs:
			if round(self.time, 4) < timeIncrements["until"]:
				self.time_inc = timeIncrements["time_inc"]
				break

	def get_time_inc(self):
		''' get the current time interval '''
		if mode.GIVEN_INTERVALS:
			for timeIncrements in self.time_incs:
				if round(self.time, 4) < timeIncrements["until"]:
					return timeIncrements["time_inc"]
		else:
			return self.time_inc

	def get_A_vert_eff_avg(self):
		''' get the Accel vert eff average '''
		A_vert_eff = equ.average(self.cur.A.vert_eff, self.prev.A.vert_eff)
		if self.prev.alt > self.ground_level:
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
		self.check_state()

	def check_state(self):
		for stage in self.stages.values():
			stage.check_state()

	def updateAlt (self, time_inc):
		self.cur.alt = equ.altitude(self.prev.alt, self.prev.V.vert, self.cur.V.vert_inc, time_inc)

	def detachEngine(self, engineName):
		self.engines[:] = [d for d in self.engines if d.get('name') != engineName]

	def updateWeight(self, time_inc):
		fuel_used = 0.0
		for stage in self.stages.values():
			fuel_used += stage.fuel_used
		self.cur.weight = self.lift_off_weight - fuel_used
		if self.cur.weight < 0:
			raise ValueError("Weight of the vehicle must be greater than 0")

	def update_V_inc(self, time_inc):
		#self.update_V_horiz_mph()
		self.update_V_vert_inc(time_inc)
		self.update_V_horiz_mph_inc(time_inc)


	def update_V_vert_inc(self, time_inc):
		self.cur.V.vert_inc = self.get_A_vert_eff_avg() * time_inc * equ.ACCEL_OF_GRAVITY

	def update_V_vert(self):
		self.cur.V.vert = self.prev.V.vert + self.cur.V.vert_inc #current or prev v inc?

	def update_V_horiz_mph_inc(self, time_inc):
		avg_A_horiz = equ.average(self.cur.A.horiz, self.prev.A.horiz)
		self.cur.V.horiz_inc = avg_A_horiz * time_inc * equ.ACCEL_OF_GRAVITY


	def update_V_horiz_mph(self):
		''' increment the Velocity horizontal '''
		self.cur.V.horiz_mph = self.prev.V.horiz_mph + self.prev.V.horiz_mph_inc


	def A_vert_formula(self, A_hv_diff):
		A_horiz = A_vert_eff = 0.0
		A = self.cur.A.total
		G = self.prev.big_G

		self.A_hv_diff = (self.prev.A.horiz + self.prev.A.vert_eff) * 0.4 -0.38
		if self.A_hv_diff < 0.020:
			self.A_hv_diff = 0.020
		A_horiz_bump = 0.01
		while A_horiz <= A_vert_eff + self.A_hv_diff:
			A_horiz = ((sqrt(2.0*A**2.0 - G**2.0))-G)/2.0 + A_horiz_bump
			A_vert = equ.pythag(None, A_horiz, A)
			A_vert_eff = A_vert - G
			A_horiz_bump += 0.01

		return A_vert_eff


	def select_A_vert_for_V_v_target(self):
		''' In order to have the rocket approach and hit a vertical velocity target,
		a vertical acceleration is chosen.
		'''
		if func.almost_equal(self.V_v_target, self.prev.V.vert, self.V_v_accuracy):
			print("V vert target of {} fps hit!".format(self.V_v_target))
			self.V_v_target_hit = True
			return 0.0
		elif self.prev.V.vert > self.V_v_target: # overshot target
			self.A_ease_in /= 1.5
			return -1.0 * self.A_ease_in
		elif self.prev.V.vert > self.V_v_target - self.V_v_target * .05: # within 5 percent of the target
			return self.A_ease_in
		else:
			return self.A_vert_formula(self.A_hv_diff)

	def select_A_vert_for_V_v_giveback(self):
		''' In order to have the rocket reduce to and hit a vertical velocity giveback target,
		a vertical acceleration is chosen.
		'''
		if not self.V_v_giveback_target_hit:
			if func.almost_equal(self.V_v_giveback_target, self.prev.V.vert, self.V_v_accuracy):
				self.V_v_giveback_target_hit = True
				return 0

			# if A_v_giveback <= -0.10 slowly approach -0.10
			# stop at -0.10 unless you've undershot
			if abs(self.prev.V.vert - self.V_v_giveback_target) < 10:
				if self.prev.V.vert > self.V_v_giveback_target:
					return -1.0 * self.A_ease_in_giveback
				else:
					self.A_ease_in_giveback /= 1.5
					return self.A_ease_in_giveback
			elif self.prev.V.vert > self.V_v_giveback_target:
				if self.A_v_giveback <= -0.10:
					self.A_v_giveback += 0.0003
				else:
					return -0.10
			return self.A_v_giveback
		else:
			return 0


	def select_A_vert(self):
		''' selects the A vert based on the current height and vert velocity '''
		if self.prev.alt <= self.tower_height:
			return "a"

		if self.V_v_start_giveback:
			return self.select_A_vert_for_V_v_giveback()
		elif self.V_v_target_hit:
			return 0
		else:
			return self.select_A_vert_for_V_v_target()

	def updateA(self):
		self.cur.A.set_raw(self.prev.force, self.cur.weight)
		self.cur.ADC_adjusted = self.prev.ADC_predicted - self.prev.ADC_error
		self.cur.A.total = self.cur.A.raw - self.cur.ADC_adjusted


	def update_ADC_actual(self, time_inc):
		self.cur.ADC_actual = equ.ADC(self.cur.V.air_speed_mph, self.cur.alt, self.adc_K)  # with resultant ADC in  "g" units
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

	def burn_fuel(self, time_inc):
		for engine in self.engines:
			engine.burn_fuel(time_inc, self.prev.alt)

	def getTotalFuelUsed(self):
		#self.fuel_used_per_stage_report()
		fuel_used = 0
		for name, stage in self.stages:
			fuel_used += stage.fuel_used
		return fuel_used

	def list_engine_names(self):
		engine_names = []
		for engine in self.engines:
			engine_names.append(engine.name)
		return engine_names

	def fuel_used_per_stage_report(self):
		''' prints a report of stage names and fuel used '''
		for name, stage in self.stages.iteritems():
			print name, stage, stage.fuel_used

	def setEngineThrottleOverride(self, engineName, throt):
		engines = self.find_engines(engineName)
		for engine in engines:
			engine.setThrottleOverride(throt)

	def setEngineThrottle(self, engineName, throt, time_inc):
		engines = self.find_engines(engineName)
		for engine in engines:
			engine.setThrottle(throt, time_inc)

	def setEngineThrottleByStage(self, engineName, throt, time_inc, stage):
		engine = self.find_engine_by_stage(engineName, stage)
		if throt == "max":
			engine.setThrottle(engine.max_throt)
		elif throt == "min":
			engine.setThrottle(engine.min_throt)
		elif throt == "off":
			engine.setThrottle(0.0)
		else:
			engine.setThrottle(throt,time_inc)


	def setEngineAssignedThrustPerEngine(self, engineName, thrust):
		engines = self.find_engines(engineName)
		for engine in engines:
			if thrust == "max":
				engine.set_assigned_thrust_per_engine(engine.thrust_sl)
			else:
				engine.set_assigned_thrust_per_engine(thrust)


	def get_engine_throttle(self, engineName):
		''' Takes an engine name string and returns that engines throttle '''
		engine = self.find_engine(engineName)
		return engine.throt

	def print_engines(self):
		''' Prints the name, count and stage of the vehicles engines '''
		for engine in self.engines:
			print engine.name, engine.engine_count, engine.stage

	def display_engine_messages(self):
		''' Prints and empties the queue of engine messages '''
		for engine in self.engines:
			for message in engine.messages:
				print (message)
			engine.messages = []

	def find_engine_by_stage(self, engineName, stage):
		''' returns the first engine with the given name and stage '''
		for engine in self.engines:
			if engine.name == engineName and engine.stage == stage:
				return engine

	def find_engine(self, engineName):
		''' returns the first engine with the given name '''
		for engine in self.engines:
			if engine.name == engineName:
				return engine

	def find_engines(self, engineName):
		''' returns all the engines with the given name '''
		engines = []
		for engine in self.engines:
			if engine.name == engineName:
				engines.append(engine)
		return engines


	def engine_status(self, engineName=None):
		''' Prints the Throttle, thrust and fuel used for every engine '''
		if engineName:
			engines = [self.find_engine(engineName)]
		else:
			engines = self.engines
		for engine in engines:
			print(engine)

	def handle_event(self, event):
		''' Takes an event object (with name and event specific keys) and calls functions relating to that '''
		event_handled = False
		if event["name"] == "Adjust Weight":
			event_handled = True
			print "Adjusting weight"
			self.lift_off_weight += event["amount"]
		if event["name"] == "Adjust Acceleration":
			event_handled = True
			print "Adjusting weight"
			self.cur.A.total += event["amount"]
		if event["name"] == "Giveback V Vert":
			event_handled = True
			print("EVENT: Starting to giveback V vert to {}fps".format(event["target"]))
			self.V_v_giveback_target = event["target"]
			self.V_v_start_giveback = True
		if not event_handled:
			message = "Event {} was not handled".format(event["name"])
			raise ValueError(message)

	def handle_stage_event(self, event):
		''' Takes an event object (with name, stage and event specific keys) and calls functions relating to that '''
		event_handled = False
		stage = self.stages[event["stage"]]
		start_time = event["start_time"] #pylint: disable=W0612
		end_time = event["end_time"] #pylint: disable=W0612

		if event["name"] == "Set Target Throttle By Stage":
			event_handled = True
			self.setEngineThrottleByStage(event["engine"], event["target"], self.get_time_inc(), event["stage"])

		if event["name"] == "Jettison":
			#func.break_point()
			event_handled = True
			stage.jettison()
			self.adc_K -= stage.adc_K
			for engine in self.engines:
				if engine.stage == stage.name:
					engine.setThrottleOverride(0)
					engine.setThrottleOverride(0)
				if engine.stage == "orbiter" and stage.name == "RLV":
					#orbiter engines use RLV as fuel source until RLV is jettisoned
					engine.set_fuel_source(self.stages["orbiter"])

		assert event_handled

	def handle_engine_event(self, event):
		''' Takes an event object (with name, engine and event specific keys) and calls functions relating to that '''
		event_handled = False
		engines = self.find_engines(event["engine"])
		start_time = event["start_time"]
		end_time = event["end_time"]
		time_inc = self.get_time_inc()
		for engine in engines:
			if event["name"] == "Change Thrust":
				event_handled = True
				if self.time < event["end_time"]:
					engine.changeThrust(event["rate"], time_inc)

			if event["name"] == "Power Down Thrust":
				event_handled = True
				engine.power_down(start_time, end_time, self.time, time_inc, self.cur.alt, event["thrusts"])

			if event["name"] == "Set Throttle Target":
				event_handled = True
				target = event["target"]
				engine.setThrottle(target, time_inc)

			if event["name"] == "Engine Cut-off":
				event_handled = True
				engine.setThrottleOverride(0.0)
				engine.setThrottleOverride(0.0)
				print("\nEVENT: {} cut-off".format(engine.name))
		assert event_handled
