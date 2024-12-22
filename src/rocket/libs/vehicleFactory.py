""" query for flight profile and spec information """

from datetime import date
import time
import copy

from colorama import Fore, Back, Style

from libs.stage import Stage
from libs.rocketEngine import RocketEngine, LiquidRocketEngine

from libs.vehicle import Vehicle

from libs.query import Query as q
from libs import fileManager as fileMan
import mode


class VehicleFactory(object):
    """Creates vehicles (heavy lift vehicles)"""

    def __init__(self):
        pass

    @classmethod
    def create_vehicle(cls, specs):
        """create a heavy lift vehicle"""
        stages = cls.init_stages(specs["stages"])
        engines = cls.create_engines(specs["engines"])
        cls.set_holding_engines(stages, engines)
        cls.set_engine_initial_fuel_source(engines, stages)

        rocket = Vehicle(specs, stages, engines)
        rocket.adc_K = cls.get_total_adc_K(specs["stages"])

        rocket.time = 0.0
        if mode.GIVEN_INTERVALS:
            time_incs_json = fileMan.load_json("save/time/time_incs.json")
            rocket.time_incs = time_incs_json["time_incs"]
            rocket.set_time_inc()
            rocket.load_time_incs = True
        else:
            rocket.time_inc = 0.1
            rocket.load_time_incs = False

        return rocket

    @classmethod
    def create_vehicle_copy(cls, old_rocket):
        """create a copy of a heavy lift vehicle"""
        new_rocket = cls.create_vehicle(old_rocket.specs)
        new_rocket.cur.alt = old_rocket.specs["initial_alt"]
        new_rocket.V_v_target = old_rocket.specs["V_v_target"]
        new_rocket.V_v_giveback_target = old_rocket.specs["V_v_giveback_target"]
        new_rocket.V_v_giveback_time = round(old_rocket.specs["V_v_giveback_time"], 1)

        new_rocket.ground_level = new_rocket.cur.alt
        new_rocket.tower_height = old_rocket.specs["tower_height"]
        # sets the initial thrusts and throttles of the engines

        for i, old_engine in enumerate(old_rocket.engines):
            new_rocket.engines[i].throt_prev = old_engine.throt_prev
            new_rocket.engines[i].throt_cur = old_engine.throt_cur
            new_rocket.engines[i].burn_rate = old_engine.burn_rate
            new_rocket.engines[i].thrust_total = old_engine.thrust_total
            new_rocket.engines[i].reached_max = old_engine.reached_max
            new_rocket.engines[i].attached = old_engine.attached
            try:
                new_rocket.engines[i].power_down_in_progress = (
                    old_engine.power_down_in_progress
                )
            except AttributeError:
                pass
            try:
                new_rocket.engines[i].power_down_start_time = (
                    old_engine.power_down_start_time
                )
                new_rocket.engines[i].burn_rate_per_engine = copy.copy(
                    old_engine.burn_rate_per_engine
                )
            except AttributeError:
                pass

        for name, old_stage in old_rocket.stages.items():
            new_rocket.stages[name].fuel_used = old_stage.fuel_used
            new_rocket.stages[name].attached = old_stage.attached

        new_rocket.cur._alt = old_rocket.cur._alt
        new_rocket.cur._big_G = old_rocket.cur._big_G
        new_rocket.cur._weight = old_rocket.cur._weight
        new_rocket.cur._ADC_predicted = old_rocket.cur._ADC_predicted
        new_rocket.cur._ADC_actual = old_rocket.cur._ADC_actual
        new_rocket.cur._ADC_error = old_rocket.cur._ADC_error
        new_rocket.cur.force = old_rocket.cur.force
        new_rocket.cur.A._horiz = old_rocket.cur.A._horiz
        new_rocket.cur.A._vert = old_rocket.cur.A._vert
        new_rocket.cur.A._total = old_rocket.cur.A._total
        new_rocket.cur.A._vert_eff = old_rocket.cur.A._vert_eff

        new_rocket.cur.V._vert = old_rocket.cur.V._vert
        new_rocket.cur.V._vert_inc = old_rocket.cur.V._vert_inc
        new_rocket.cur.V._horiz = old_rocket.cur.V._horiz
        new_rocket.cur.V._horiz_inc = old_rocket.cur.V._horiz_inc
        new_rocket.cur.V._total = old_rocket.cur.V._total

        new_rocket.load_time_incs = old_rocket.load_time_incs
        new_rocket.V_v_target_hit = old_rocket.V_v_target_hit
        new_rocket.V_v_start_giveback = old_rocket.V_v_start_giveback
        new_rocket.V_v_giveback_target_hit = old_rocket.V_v_giveback_target_hit
        new_rocket.A_v_giveback = old_rocket.A_v_giveback
        new_rocket.time = old_rocket.time

        new_rocket.A_ease_in = old_rocket.A_ease_in
        new_rocket.A_ease_in_giveback = old_rocket.A_ease_in_giveback
        new_rocket.A_hv_diff = old_rocket.A_hv_diff

        return new_rocket

    @classmethod
    def set_holding_engines(cls, stages, engines):
        """adds the appropriate engines to each stage"""
        for stage in stages.values():
            for engine in engines:
                if engine.stage == stage.name:
                    stage.attach_engine(engine)

    @classmethod
    def get_total_adc_K(cls, stages):
        """totals the adc_Ks of the given stages
        "stages" is a dict with Stage names as keys and stage specs as values
        """
        adc_K = 0.0
        for stage_values in stages.values():
            adc_K += stage_values["adc_K"]
        return adc_K

    @staticmethod
    def load_available_engines():
        """Loads the available engine json datafile"""
        available_engines_json = fileMan.load_json("save/engine/rocketEngineData.json")
        return available_engines_json["rocketEngines"]

    @classmethod
    def load_engine_data(cls, selected_engines):
        """Takes a json object with the engine_name and engine_count and loads the matching
        engine data to a json object.
        """
        available_engines = cls.load_available_engines()
        engines = []
        for selected_engine in selected_engines:
            try:
                name = selected_engine["engine_name"]
                engine_data = copy.copy(available_engines[name])
                engine_data["name"] = name
                engine_data.update(selected_engine)
                engines.append(engine_data)
            except KeyError:
                print("ERROR Engine {} not found".format(name))
        return engines

    @classmethod
    def init_stages(cls, stage_data):
        stages = {}
        for stage_type, stage_datum in stage_data.items():
            stages[stage_type] = Stage(stage_datum)
        return stages

    @staticmethod
    def set_engine_initial_fuel_source(engines, stages):
        for engine in engines:
            if engine.name == "SRM":
                engine.set_fuel_source(stages["R-SRB"])
                stages["R-SRB"].fueling(engine)
            elif engine.name == "SRMU":
                engine.set_fuel_source(stages["E-SRB"])
                stages["E-SRB"].fueling(engine)
            elif engine.stage == "LFB":
                engine.set_fuel_source(stages["LFB"])
                stages["LFB"].fueling(engine)
            else:
                engine.set_fuel_source(stages["RLV"])
                stages["RLV"].fueling(engine)

    @classmethod
    def create_engine(cls, engine_data):
        engine = RocketEngine.factory(engine_data)
        return engine

    @classmethod
    def create_engines(cls, selected_engines):
        """loads engine data from file matching the given names"""
        engine_data = cls.load_engine_data(selected_engines)
        engines = []
        for engine in engine_data:
            engines.append(cls.create_engine(engine))
        return engines

    @classmethod
    def select_engines(cls, stage_name, stage_jettison_time, fuel_type):
        engines = cls.load_available_engines()
        compatable_engines = []
        selected_engines = []
        for engine_name, engine_data in engines.items():
            if (
                fuel_type is None
                or fuel_type == engine_data["type"]
                and stage_name in engine_data["stages"]
            ):
                compatable_engines.append({engine_name: engine_data})

        for engine in compatable_engines:
            engine_name = list(engine)[0]
            count = float(
                q.query_int("How many {} {}s? ".format(stage_name, engine_name))
            )

            if count > 0:
                this_engine = cls.collect_engine_details(
                    engine, stage_name, stage_jettison_time
                )
                this_engine["engine_count"] = count
                selected_engines.append(this_engine)
                print(
                    "{} {} engines are now attached to the {}.".format(
                        int(count), this_engine["engine_name"], stage_name
                    )
                )

        return selected_engines

    @classmethod
    def collect_engine_details(cls, engine_data, stage_name, stage_jettison_time):
        engine_name = list(engine_data)[0]
        this_engine = {}
        # only accept integer values but store as float for compatibility
        this_engine["engine_name"] = engine_name
        this_engine["stage"] = stage_name
        ignition_time = None
        if stage_name == "E-SRB" or stage_name == "R-SRB":
            this_engine["starting_throttle"] = 1.0
            return this_engine

        starting_throttle = q.query_min_max(
            "{} {} Throttle at 0.00 seconds (lift-off) (typically {})? ".format(
                stage_name, engine_name, engine_data[engine_name]["typical_throt_at_0"]
            )
        )

        if starting_throttle == 0.0:
            ignition_time = q.query_float(
                "Engine ignition time (Press enter to select a default value of never): ",
                float("inf"),
            )

        if ignition_time == float("inf") and starting_throttle == 0:
            print("This engine is not used during the sim.")
            return this_engine

        if stage_name != "orbiter":
            power_down_start_time = q.query_float(
                "{} {} Time to begin throttle down: ".format(stage_name, engine_name)
            )
        else:
            power_down_start_time = float("inf")
        this_engine["starting_throttle"] = starting_throttle
        this_engine["power_down_start_time"] = power_down_start_time
        this_engine["ignition_time"] = ignition_time
        engine_data[engine_name].update(this_engine)
        temp_engine = LiquidRocketEngine(engine_data[engine_name])

        stats = temp_engine.engine_stats(
            starting_throttle, power_down_start_time, ignition_time, stage_jettison_time
        )

        print(
            "Max throttle of {:.2f} reached at {:.1f} seconds".format(
                engine_data[engine_name]["max_throt"], stats["max_reached_time"]
            )
        )
        if power_down_start_time == float("inf"):
            print("Throttle down does not occur during the sim. ")
        else:
            print(
                "Throttle down will begin at {:.1f} seconds".format(
                    power_down_start_time
                )
            )
        if stage_name != "orbiter":
            if stats["throttle_at_end_time"] > 0:
                print(
                    "Engine throttle at jettison is {:.1f}".format(
                        stats["throttle_at_end_time"]
                    )
                )
            else:
                print(
                    "Engine throttle will reach min at {:.1f} seconds".format(
                        stats["min_reached_time"]
                    )
                )
                print(
                    "Engine throttle will cut-off at {:.1f} seconds".format(
                        stats["engine_cutoff_time"]
                    )
                )

        edit_again = q.query_yes_no("Discard changes and edit this field again?", "no")
        if edit_again:
            return cls.collect_engine_details(
                engine_data, stage_name, stage_jettison_time
            )
        else:
            return this_engine

    @staticmethod
    def collect_launch_pad():
        """queries and stores event info regarding the initial alt and tower height"""
        initial_alt = q.query_float("What is initial alt? ")
        tower_height = q.query_float("What is tower height?  ")
        return {"initial_alt": initial_alt, "tower_height": tower_height}

    @staticmethod
    def collect_goals():
        """queries and stores the vertical velocity target"""
        V_v_target = q.query_float(
            "What is desired V vert target (typically 2000fps)? "
        )
        print("\nGiveback V Vert Event\n")
        V_v_giveback_target = q.query_float(
            "What is desired V vert target (typically 1200fps)? "
        )
        V_v_giveback_time = q.query_float("Giveback start time (typically 205.50): ")
        return {
            "V_v_target": V_v_target,
            "V_v_giveback_target": V_v_giveback_target,
            "V_v_giveback_time": V_v_giveback_time,
        }

    @staticmethod
    def collect_version():
        """get the version (used for the file name)"""
        today = date.fromtimestamp(time.time())

        version_name = q.query_string(
            "What is the version date (hit enter for today's date)? ",
            today.strftime("%m-%d-%Y"),
        )
        return {"version_name": version_name}
