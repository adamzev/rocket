from math import sqrt
import copy


from vehicle import Vehicle
from stage import Stage
from rocketEngine import RocketEngine

import generalEquations as equ
from util.text_interface import *
import util.func as func
import libs.query as q
from libs import fileManager as fileMan


class VehicleFactory():
	''' Creates vehicles (heavy lift vehicles) '''
	def __init__():
		pass


	@classmethod
	def create_vehicle(cls, specs, load_time_incs=False):
		rocket = Vehicle(specs, load_time_incs=False)
		stages = cls.init_stages(specs["stages"])
		rocket.stages = stages

		engines = []
		cls.attach_engines(specs["engines"])
		cls.set_engine_initial_fuel_source()
		cls.set_adc_K(specs["stages"])

		return rocket


	@staticmethod
	def select_engine_from_list(stage_name=None, fuel_type=None):
		''' select an engine from a list
		Returns False if the user is done entering engines
		'''
		engines = self.load_available_engines()
		compatable_engines = []
		for key, value in engines.iteritems():
			if fuel_type == None or fuel_type == value['type']:
				compatable_engines.append({key:value})

		selected_engines = q.query_from_list("engine", "Select an engine number: ", compatable_engines, True, lambda x: RocketEngine.collect_engine_details(x, stage_name))
		return selected_engines
	
	@staticmethod
	def load_available_engines():
		''' Loads the available engine json datafile '''
		available_engines_json = fileMan.load_json("save/engine/rocketEngineData.json")
		return available_engines_json["rocketEngines"]

	@staticmethod
	def load_engine_data(selected_engines):
		''' Takes a json object with the engine_name and engine_count and loads the matching
		engine data to a json object.
		'''
		available_engines = self.load_available_engines()
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

	def set_engine_initial_fuel_source(self):
		for engine in self.engines:
			if engine.type == "Solid":
				engine.set_fuel_source(self.stages["SRB"])
				self.stages["SRB"].fueling(engine)
			elif engine.stage == "LFB":
				engine.set_fuel_source(self.stages["LFB"])
				self.stages["LFB"].fueling(engine)
			else:
				engine.set_fuel_source(self.stages["RLV"])
				self.stages["RLV"].fueling(engine)



	@classmethod
	def create_engine(cls, engine_data):
		engine = RocketEngine.factory(engine_data)
		return engine

	@classmethod
	def create_engines(cls, selected_engines):
		''' loads engine data from file matching the given names
		'''
		engine_data = Vehicle.load_engine_data(selected_engines)
		engines = []
		for engine in engine_data:
			engines.append(cls.create_engine(engine))
		return engines


	def select_engines(stage_name, fuel_type):
		return Vehicle.select_engine_from_list(stage_name, fuel_type)

	def fueling(self, engine):
		self.fueling_engines.append(engine)
	def __str__(self):
		return "Stage Name = {} Fuel Remaining = {} Burn Rate = {}".format(self.name, self.get_fuel_remaining(), self.get_fuel_burn_rate())
