import os

os.chdir("/home/tutordelphia/www/rocket")

from libs.vehicleFactory import VehicleFactory as VF
from util.func import almost_equal, pretty_json



def test_collect_engine_details():
	specs = {
		"name": "HLV test",
		"earth_rotation_mph": 912.67,
		"MK": "2-45",
		"lift_off_weight": 25417828.59,
		"stages": {
			"SRB": {
				"name": "SRB",
				"fuel_type": "Solid",
				"attached": True,
				"jettison_weight": 400000,
				"preburned": 0,
				"initial_weight": 2225000,
				"fuel": 1825000,
				"adc_K": 0.142,
				"lift_off_weight": 2225000,
				'jettison_time' : ""

			},
			"orbiter": {
				"name": "orbiter",
				"fuel_type": "Liquid",
				"attached": True,
				"jettison_weight": 0,
				"preburned": 0,
				"initial_weight": 3000000,
				"fuel": 3000000,
				"adc_K": 0.475,
				"lift_off_weight": 3000000,
				'jettison_time' : ""
			},
			"RLV": {
				"name": "RLV",
				"fuel_type": "Liquid",
				"attached": True,
				"jettison_weight": 2256890,
				"preburned": 51966.7,
				"initial_weight": 13681275,
				"fuel": 11372418.3,
				"adc_K": 1.419,
				"lift_off_weight": 13629308.3,
				'jettison_time' : 218.1418
			},
			"LFB": {
				"name": "LFB",
				"fuel_type": "Liquid",
				"attached": True,
				"jettison_weight": 749168,
				"preburned": 30204.71,
				"initial_weight": 6593725,
				"fuel": 5814352.29,
				"adc_K": 0.35,
				"lift_off_weight": 6563520.29,
				'jettison_time' : 138.83
			}
		}
	}

	selected_engines = []
	for stage_name, stage_data in specs["stages"].items():
		selected_engines += VF.select_engines(stage_name, stage_data["jettison_time"], stage_data["fuel_type"])

	specs.update({
		"engines" : selected_engines,
	})

	pretty_json(specs)


def main():
	test_collect_engine_details()


if __name__ == '__main__':
	main()
