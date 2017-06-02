from math import sqrt
import copy



from stage import Stage
from rocketEngine import RocketEngine

import generalEquations as equ

import util.func as func

from libs.vehicle import Vehicle

from libs.query import Query as q
from libs import fileManager as fileMan


class VehicleFactory(object):
	''' Creates vehicles (heavy lift vehicles) '''
	def __init__(self):
		pass


	@classmethod
	def create_vehicle(cls, specs, load_time_incs=False):
		''' create a heavy lift vehicle '''
		stages = cls.init_stages(specs["stages"])
		engines = cls.create_engines(specs["engines"])
		cls.set_holding_engines(stages, engines)
		cls.set_engine_initial_fuel_source(engines, stages)
		for stage in stages.values():
			stage.attached_engine_report()

		rocket = Vehicle(specs, stages, engines)
		rocket.adc_K = cls.get_total_adc_K(specs["stages"])

		rocket.time = 0.0
		if load_time_incs:
			time_incs_json = fileMan.load_json('save/time/time_incs.json')
			rocket.time_incs = time_incs_json['time_incs']
			rocket.set_time_inc()
			rocket.load_time_incs = True
		else:
			rocket.time_inc = 0.1
			rocket.load_time_incs = False


		return rocket

	@classmethod
	def set_holding_engines(cls, stages, engines):
		''' adds the appropriate engines to each stage '''
		for stage in stages.values():
			for engine in engines:
				if engine.stage == stage.name:
					stage.attach_engine(engine)
	@classmethod
	def get_total_adc_K(cls, stages):
		''' totals the adc_Ks of the given stages
			"stages" is a dict with Stage names as keys and stage specs as values
		'''
		adc_K = 0.0
		for stage_values in stages.values():
			adc_K += stage_values["adc_K"]
		return adc_K


	@classmethod
	def select_engine_from_list(cls, stage_name=None, fuel_type=None):
		''' select an engine from a list
			Returns False if the user is done entering engines
		'''
		engines = cls.load_available_engines()
		compatable_engines = []
		for key, value in engines.iteritems():
			if fuel_type is None or fuel_type == value['type']:
				compatable_engines.append({key:value})

		list_name = "engine"
		intro = "Select an engine number: "
		if stage_name:
			list_name = "{} engine".format(stage_name)
			intro = "Select an engine number to add to the {}: ".format(stage_name)

		selected_engines = q.query_from_list(
			list_name,
			intro,
			compatable_engines,
			True,
			lambda x: cls.collect_engine_details(x, stage_name)
		)
		return selected_engines

	@staticmethod
	def load_available_engines():
		''' Loads the available engine json datafile '''
		available_engines_json = fileMan.load_json("save/engine/rocketEngineData.json")
		return available_engines_json["rocketEngines"]

	@classmethod
	def load_engine_data(cls, selected_engines):
		''' Takes a json object with the engine_name and engine_count and loads the matching
			engine data to a json object.
		'''
		available_engines = cls.load_available_engines()
		engine_data = []
		for selected_engine in selected_engines:
			name = selected_engine["engine_name"]
			count = selected_engine["engine_count"]
			stage = selected_engine["stage"]

			try:
				engine = copy.copy(available_engines[name])
				engine["engine_count"] = count
				engine["name"] = name
				engine["stage"] = stage
				engine_data.append(engine)
			except KeyError:
				print ("ERROR Engine {} not found".format(name))
		func.pretty_json(engine_data)
		return engine_data


	@classmethod
	def init_stages(cls, stage_data):
		stages = {}
		for stage_type, stage_datum in stage_data.iteritems():
			stages[stage_type] = Stage(stage_datum)
		return stages

	@staticmethod
	def set_engine_initial_fuel_source(engines, stages):
		for engine in engines:
			if engine.type == "Solid":
				engine.set_fuel_source(stages["SRB"])
				stages["SRB"].fueling(engine)
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
		''' loads engine data from file matching the given names
		'''
		engine_data = cls.load_engine_data(selected_engines)
		engines = []
		for engine in engine_data:
			engines.append(cls.create_engine(engine))
		return engines

	@classmethod
	def select_engines(cls, stage_name, fuel_type):
		return cls.select_engine_from_list(stage_name, fuel_type)

	@staticmethod
	def collect_engine_details(engine_data, stage_name):
		func.pretty_json(engine_data)
		engine_name = engine_data.keys()[0]
		# only accept integer values but store as float for compatibility
		count = float(q.query_int("How many {}s? ".format(engine_name)))
		this_engine = {}
		this_engine["engine_count"] = count
		this_engine["engine_name"] = engine_name
		this_engine["stage"] = stage_name
		print("{} {} engines are now attached.".format(int(count), this_engine["engine_name"]))
		return this_engine
