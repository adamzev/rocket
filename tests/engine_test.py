import unittest

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from rocket.libs import rocketEngine as eng

rdData = {
	"ignition_time": None,
	"starting_throttle": 0.7,
	"power_down_start_time": 135.9,
	"stage": "RLV",
	"name": "RD171",
	"thrust_sl"  : 1632000.0,
	"thrust_vac" : 1777000.0,
	"lbm_dry" : 20503,
	"fuel" : 5932224.827,
	"min_throt" : 0.56,
	"typical_throt_at_0" : 0.7,
	"max_throt" : 1.0,
	"engine_count" : 1.0,
	"throt_rate_of_change_limit" : 0.15,
	"burn_rate" : 5270.0,
	"stages" : {
		"LFB" : "default",
		"RLV" : "default"
	},
	"type" : "Liquid"
}

ssData = {
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"min_throt" : 0.56,  #check value
		"max_throt" : 0.95,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15, #check value
		"engine_count" : 1.0,
		"fuel" : 0.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	}

rdEng = eng.RocketEngine(rdData)
ssEng = eng.RocketEngine(ssData)

SRM_data =	{
		"name": "SRM",
		"thrust_sl"  : 3600000.0,
		"thrust_vac" : 3600000.0,
		"min_throt" : 0.56,
		"max_throt" : 1.0,
		"engine_count" : 4.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"burn_rate" : 14876.0325,
		"assigned_thrust" : 0.0,
		"specImp_sl" : 242.00,
		"specImp_vac" : 268.20,
		"thrust_controlled" : True
	}

SRM = eng.RocketEngine(SRM_data)
# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold


class EngineTests(unittest.TestCase):
	def test_thrust_RD_sea_level(self):
		rdEng.setThrottleOverride(1)
		rdEng.setThrottleOverride(1)
		self.assertEqual(rdEng.thrustAtAlt(0), 1632000)

	def test_thrust_RD_30000(self):
		rdEng.setThrottleOverride(1)
		rdEng.setThrottleOverride(1)
		assert almost_equal(rdEng.thrustAtAlt(30000), 1733940.707, 0.001)

	def test_thrust_SS_sea_level(self):
		ssEng.setThrottleOverride(0.95)
		ssEng.setThrottleOverride(0.95)
		assert almost_equal(ssEng.thrustAtAlt(0), 397223.5, 0.001)

	def test_thrust_SS_12000(self):
		ssEng.setThrottleOverride(0.95)
		ssEng.setThrottleOverride(0.95)
		assert almost_equal(ssEng.thrustAtAlt(12000), 429827.1905, 0.001)

	def test_specImp(self):
		alt = 2491.84
		expected_result = 244.205664
		assert almost_equal(SRM.specific_impulse_at_alt(alt), expected_result, 0.1)

	def test_fuel_used_in_startup(self):
		alt = 0
		rdEng.setThrottleOverride(0.56)
		rdEng.setThrottleOverride(0.56)
		fuel_used = 0
		time_inc = 0.1
		while rdEng.throt_avg < 1:
			rdEng.setThrottle(1, time_inc)
			fuel_used += rdEng.get_eff_fuel_burn_rate() * time_inc
		expected_result = 12057.760
		assert almost_equal(fuel_used, expected_result, 0.0000000001)

	def test_fuel_used_in_startup_full_shutdown(self):
		alt = 0
		rdEng.setThrottleOverride(0.74)
		rdEng.setThrottleOverride(0.74)
		fuel_used = 0
		time_inc = 0.1
		time = 0
		while rdEng.throt_avg < 1:
			time += time_inc
			rdEng.setThrottle(1, time_inc)
			fuel_used += rdEng.get_eff_fuel_burn_rate() * time_inc

		while time < 145.8667:
			time += time_inc
			fuel_used += rdEng.get_eff_fuel_burn_rate() * time_inc

		while rdEng.throt_avg > 0:
			time += time_inc
			rdEng.setThrottle(0, time_inc)
			fuel_used += rdEng.get_eff_fuel_burn_rate() * time_inc

		expected_result = 779587.76
		assert almost_equal(fuel_used, expected_result, 1000)


	def test_engine_stats(self):
		stats = {
			"max_reached_time": 2.0,
			"min_reached_time": 138.8,
			"engine_cutoff_time": 138.9,
			"throttle_at_end_time": 0.0
		}
		liq_eng = eng.LiquidRocketEngine(rdData)
		results = liq_eng.engine_stats(0.7, 135.9, None, 139.1)
		for key in stats:
			assert almost_equal(stats[key], results[key])




if __name__ == '__main__':
	unittest.main()
