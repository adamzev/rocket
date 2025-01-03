from math import sqrt

from colorama import Fore, Style


import generalEquations as equ

from libs.physicalStatus import PhysicalStatus
from libs import fileManager as fileMan

import util.func as func
import mode


class Vehicle(object):

    def __init__(self, specs, stages, engines):
        earth_rotation_mph = specs["earth_rotation_mph"]
        self.cur = PhysicalStatus(alt=0, earth_rotation_mph=earth_rotation_mph)
        self.prev = PhysicalStatus(alt=0, earth_rotation_mph=earth_rotation_mph)
        self.specs = specs
        self.time_incs = {}
        self.time_inc = 0.1
        self.max_A_v = 0.75
        self.stages = stages
        self.engines = engines
        self.given_time_incs = mode.GIVEN_INTERVALS
        self.V_v_target_hit = False  # Has the rocket hit the V_v target
        self.V_v_start_giveback = False
        self.V_v_giveback_target_hit = (
            False  # Has the rocket hit the V_v giveback target
        )
        self.A_v_giveback = -0.4
        self.V_v_target = 0.0
        self.V_v_giveback_target = 0.0
        self.V_v_giveback_time = None
        self.A_vh_scale_factor = 1.0
        self.time = 0
        self.cur.V.horiz_mph = earth_rotation_mph
        self.A_ease_in = (
            0.1  # used to adjust the acceleration to ease in to the target V_v
        )
        self.A_ease_in_giveback = 0.1
        self.cur.V.vert = 0.0
        self.tower_height = 0
        self.ground_level = 0.0  # overwriten by initial alt
        self.adc_K = 0.0
        self.cur.A.horiz = 0.0
        self.cur.A.vert = 0.0
        self.V_v_accuracy = 0.0000001
        self.A_hv_diff = 0.0
        self.lift_off_weight = self.sum_stage_weights()
        self.cur.weight = self.lift_off_weight
        self.copy_status()
        self.name = "{} MK {}".format(specs["name"], specs["MK"])

    def sum_stage_weights(self):
        total = 0
        for stage in self.stages.values():
            total += stage.lift_off_weight
        return total

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
        sign_symb = "+" if self.cur.V.vert_inc >= 0 else ""
        row1 = "-" * 140 + "\n"
        row2 = "{:>48,.6f}      {:>6,.8f}     G={: <12,.8f}\n".format(
            self.cur.A.total, self.cur.ADC_actual, big_G
        )
        time_string = "{:<6,.1f}".format(self.time)
        time_string = Fore.RED + time_string + Style.RESET_ALL
        row3 = "{}{:<12,.2f} {:5} WT={:<13,.2f}->{:>9,.6f}      {:<12,.8f}   Vh={:<12,.6f} Vas={:<12,.3f}     {:<12,.6f} {:<10,.8f}\n".format(
            sign_symb,
            self.cur.V.vert_inc,
            time_string,
            self.cur.weight,
            self.cur.A.raw,
            ADC_adj,
            self.cur.V.horiz_mph,
            V_as,
            A_v,
            A_h,
        )
        alt_string = "ALT={:<,.1f}'".format(alt)
        row4 = '{:<13,.6f} {:<16} T={:<19,.4f}  "{:<,.4f}"\n'.format(
            V_vert, alt_string, thrust, ADC_guess
        )
        return row1 + row2 + row3 + row4

    def save_current_row(self, first=False):
        """Saves the current row to a csv file"""
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
            self.cur.A.total,
        )
        row2 = "{:.8f}, {:.5f}, {:.10f}, {:.6f}, {:.6f}, {:.1f}, {:.8f}\n".format(
            A_h, A_v, big_G, V_as, self.cur.V.horiz_mph, self.cur.V.vert_inc, V_vert
        )
        headers = "time, alt, thrust, weight, ADC_guess, ADC_actual, ADC_adj, ADC_error, A_raw, A_total, A_h, A_v, bigG, V_as, V_horiz_mph, V_vert_inc, V_vert \n"
        if first:
            fileMan.create_csv(headers, "data/rows.csv")
        fileMan.update_csv(row1 + row2, "data/rows.csv")

    def get_assigned_A_vert(self):
        """sets the assigned A vert based on the current time and the time_incs object"""
        for A_vert_assigned_by_time in self.assigned_A_vert:
            # this may need to be <= instead of < to get the correct A_vert
            # since time incs get added on after but the assigned A_vert is
            # used for the current row
            if round(self.time, 6) <= A_vert_assigned_by_time["until"]:
                return A_vert_assigned_by_time["A_vert"]
        raise ValueError("No assigned A_vert found for time {}".format(self.time))

    def set_time_inc(self):
        """sets the current time increment based on the current time and the time_incs object"""
        for timeIncrements in self.time_incs:
            if round(self.time, 6) < timeIncrements["until"]:
                self.time_inc = timeIncrements["time_inc"]
                break

    def get_time_inc(self):
        """get the current time interval"""
        if mode.GIVEN_INTERVALS:
            for timeIncrements in self.time_incs:
                if round(self.time, 6) < timeIncrements["until"]:
                    return timeIncrements["time_inc"]
        else:
            return self.time_inc

    def get_A_vert_eff_avg(self):
        """get the Accel vert eff average"""
        A_vert_eff = equ.average(self.cur.A.vert_eff, self.prev.A.vert_eff)
        if self.prev.alt > self.ground_level:
            return A_vert_eff
        else:
            if (
                A_vert_eff < 0
            ):  # Not enough force to lift off, but don't move down if on the ground
                return 0.0
            else:
                return A_vert_eff  # enough force to lift off

    def copy_status(self):
        self.prev._alt = self.cur._alt
        try:
            self.prev._big_G = self.cur._big_G
        except AttributeError:
            pass
        self.prev._weight = self.cur._weight
        self.prev._ADC_predicted = self.cur._ADC_predicted
        self.prev._ADC_actual = self.cur._ADC_actual
        self.prev._ADC_error = self.cur._ADC_error
        self.prev.force = self.cur.force
        self.prev.A._horiz = self.cur.A._horiz
        self.prev.A._vert = self.cur.A._vert
        self.prev.A._total = self.cur.A._total
        self.prev.A._vert_eff = self.cur.A._vert_eff
        self.prev.V._vert = self.cur.V._vert
        self.prev.V._vert_inc = self.cur.V._vert_inc
        self.prev.V._horiz = self.cur.V._horiz
        self.prev.V._horiz_inc = self.cur.V._horiz_inc
        self.prev.V._total = self.cur.V._total

    def tick(self):
        if self.given_time_incs:
            self.set_time_inc()
        self.time += self.time_inc

        self.copy_status()

        self.cur = PhysicalStatus()
        self.check_state()

    def check_state(self):
        for stage in self.stages.values():
            stage.check_state()

    def updateAlt(self, time_inc):
        self.cur.alt = equ.altitude(
            self.prev.alt, self.prev.V.vert, self.cur.V.vert_inc, time_inc
        )

    def detachEngine(self, engineName):
        self.engines[:] = [d for d in self.engines if d.get("name") != engineName]

    def updateWeight(self, time_inc):
        fuel_used = 0.0
        for stage in self.stages.values():
            fuel_used += stage.fuel_used
        self.cur.weight = self.lift_off_weight - fuel_used
        if self.cur.weight < 0:
            raise ValueError("Weight of the vehicle must be greater than 0")

    def update_V_inc(self, time_inc):
        # self.update_V_horiz_mph()
        self.update_V_vert_inc(time_inc)
        self.update_V_horiz_mph_inc(time_inc)

    def update_V_vert_inc(self, time_inc):
        self.cur.V.vert_inc = (
            self.get_A_vert_eff_avg() * time_inc * equ.ACCEL_OF_GRAVITY
        )

    def update_V_vert(self):
        self.cur.V.vert = (
            self.prev.V.vert + self.cur.V.vert_inc
        )  # current or prev v inc?

    def update_V_horiz_mph_inc(self, time_inc):
        avg_A_horiz = equ.average(self.cur.A.horiz, self.prev.A.horiz)
        self.cur.V.horiz_inc = avg_A_horiz * time_inc * equ.ACCEL_OF_GRAVITY

    def update_V_horiz_mph(self):
        """increment the Velocity horizontal"""
        self.cur.V.horiz_mph = self.prev.V.horiz_mph + self.prev.V.horiz_mph_inc

    def A_vert_formula(self, scale_factor):
        A_horiz = A_vert_eff = 0.0
        A = self.cur.A.total
        G = self.prev.big_G
        X = ((sqrt(2.0 * A**2.0 - G**2.0)) - G) / 2.0

        Vv = self.prev.V.vert

        if self.time <= 18.0:
            if Vv >= 400.0:
                self.max_A_v = 0.61035
            else:
                self.max_A_v = 0.65
        elif self.time <= 48.0:
            if Vv >= 1000.0:
                self.max_A_v = 0.61035
            else:
                self.max_A_v = 0.70
        elif self.time <= 75.0:
            if Vv >= 1000.0:
                self.max_A_v = 0.61035
            else:
                self.max_A_v = 0.75

        if X < 0.4:
            self.A_hv_diff = 0.001
        elif X < 0.68:
            self.A_hv_diff = 0.5 * X - 0.2
        elif X < 0.79:
            self.A_hv_diff = X - 0.54
        elif X < 0.89:
            self.A_hv_diff = 1.3 * X - 0.776
        else:
            return self.max_A_v

        A_horiz_bump = 0.002
        while A_horiz <= A_vert_eff + self.A_hv_diff * scale_factor:
            A_horiz = X + A_horiz_bump
            A_vert = equ.pythag(None, A_horiz, A)
            A_vert_eff = A_vert - G
            A_horiz_bump += 0.002

        if A_vert_eff > self.max_A_v:
            return self.max_A_v
        else:
            return A_vert_eff

    def select_A_vert_for_V_v_target(self):
        """In order to have the rocket approach and hit a vertical velocity target,
        a vertical acceleration is chosen.
        """
        if func.almost_equal(self.V_v_target, self.prev.V.vert, self.V_v_accuracy):
            print("V vert target of {} fps hit!".format(self.V_v_target))
            self.V_v_target_hit = True
            return 0.0
        elif self.prev.V.vert > self.V_v_target:  # overshot target
            self.A_ease_in /= 1.5
            return -1.0 * self.A_ease_in
        elif (
            self.prev.V.vert > self.V_v_target - self.V_v_target * 0.05
        ):  # within 5 percent of the target
            return self.A_ease_in
        else:
            return self.A_vert_formula(self.A_vh_scale_factor)

    def select_A_vert_for_V_v_giveback(self):
        """In order to have the rocket reduce to and hit a vertical velocity giveback target,
        a vertical acceleration is chosen.
        """
        if not self.V_v_giveback_target_hit:
            if func.almost_equal(
                self.V_v_giveback_target, self.prev.V.vert, self.V_v_accuracy
            ):
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
        """selects the A vert based on the current height and vert velocity"""
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
        self.cur.ADC_actual = equ.ADC(
            self.cur.V.air_speed_mph, self.cur.alt, self.adc_K
        )  # with resultant ADC in  "g" units
        # self.ADC_prediction_report()
        self.cur.ADC_error = self.prev.ADC_predicted - self.cur.ADC_actual

    def ADC_prediction_report(self):
        print(
            "Actual ADC={} prev predictedADC={} cur predictedADC = {} error={}".format(
                self.cur.ADC_actual,
                self.prev.ADC_predicted,
                self.cur.ADC_predicted,
                self.cur.ADC_error,
            )
        )

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
        # self.fuel_used_per_stage_report()
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
        """prints a report of stage names and fuel used"""
        for name, stage in self.stages.items():
            print(name, stage, stage.fuel_used)

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
            engine.setThrottle(throt, time_inc)

    def setEngineAssignedThrustPerEngine(self, engineName, thrust):
        engines = self.find_engines(engineName)
        for engine in engines:
            if thrust == "max":
                engine.set_assigned_thrust_per_engine(engine.thrust_sl)
            else:
                engine.set_assigned_thrust_per_engine(thrust)

    def get_engine_throttle(self, engineName):
        """Takes an engine name string and returns that engines throttle"""
        engine = self.find_engine(engineName)
        return engine.throt

    def print_engines(self):
        """Prints the name, count and stage of the vehicles engines"""
        for engine in self.engines:
            print(engine.name, engine.engine_count, engine.stage)

    def display_engine_messages(self):
        """Prints and empties the queue of engine messages"""
        for engine in self.engines:
            for message in engine.messages:
                print(message)
            engine.messages = []

    def find_engine_by_stage(self, engineName, stage):
        """returns the first engine with the given name and stage"""
        for engine in self.engines:
            if engine.name == engineName and engine.stage == stage:
                return engine

    def find_engine(self, engineName):
        """returns the first engine with the given name"""
        for engine in self.engines:
            if engine.name == engineName:
                return engine

    def find_engines(self, engineName):
        """returns all the engines with the given name"""
        engines = []
        for engine in self.engines:
            if engine.name == engineName:
                engines.append(engine)
        return engines

    def engine_status(self, engineName=None):
        """Prints the Throttle, thrust and fuel used for every engine"""
        if engineName:
            engines = [self.find_engine(engineName)]
        else:
            engines = self.engines
        for engine in engines:
            print(engine)

    def handle_engine_events(self):
        for engine in self.engines:
            engine.events(self.time, self.get_time_inc())

    def handle_stage_events(self):
        for stage_name, stage in self.stages.items():
            stage.events(self.time, self.get_time_inc())


    def check_v_v_giveback_time(self):
        if self.V_v_giveback_time and func.almost_equal(self.time, self.V_v_giveback_time, 0.001):
            self.V_v_start_giveback = True

    def process_srb_engines(self, SRB):
        if SRB.attached:
            remaining = SRB.get_fuel_remaining()
            for engine in SRB.attached_engines:
                remaining_per_engine = remaining / engine.engine_count
                if (
                    engine.attached
                    and (
                        remaining_per_engine
                        - engine.burn_rate
                        * self.get_time_inc()
                        / engine.engine_count
                    )
                    <= engine.power_down_fuel_level
                ):
                    if not engine.power_down_start_time:
                        print(
                            "EVENT: {} Power down started at {} seconds with fuel level {} lbm per engine".format(
                                engine.name, self.time, remaining_per_engine
                            )
                        )
                        engine.power_down_start_time = self.time
                    engine.power_down_by_burn_rates(
                        self.time, self.cur.alt, SRB
                    )

    
    def handle_srb_events(self):
        try:
            for srb_type in ["R-SRB", "E-SRB"]:
                SRB = self.stages[srb_type]
                self.process_srb_engines(SRB)
        except KeyError:
            pass  # if no stage named SRB, don't handle it

    def check_and_adjust_throttle(self):
        if self.cur.A.total > 2:
            print(f"Total acceleration exceeded 2 Gs: {self.cur.A.total} Gs")
            for engine in self.engines:
                if engine.stage == "RLV" and engine.attached:
                    # Calculate the new throttle value, reducing the current throttle by 1%
                    new_throttle_value = engine.throt_cur * 0.99
                    # Adjust the throttle using setThrottle, which considers the rate of change limit
                    engine.setThrottle(new_throttle_value, self.get_time_inc())
                    print(f"Adjusted {engine.name} throttle to {new_throttle_value:.2f} (reduced by 1%) due to exceeding acceleration limit.")



    def events(self):
        """handles automatic events like auto power up"""
        self.handle_engine_events()
        self.handle_stage_events()
        self.check_v_v_giveback_time()
        self.handle_srb_events()
        self.check_and_adjust_throttle()



