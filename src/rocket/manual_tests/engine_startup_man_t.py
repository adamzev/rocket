import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from libs import rocketEngine as eng

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

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold


def test_fuel_used_in_startup():
	alt = 0
	rdEng.setThrottleOverride(0.56)
	rdEng.setThrottleOverride(0.56)
	fuel_used = 0
	time_inc = 0.1
	time = 0
	while rdEng.throt_avg < 1:
		
		fuel_used += rdEng.get_eff_fuel_burn_rate() * time_inc
		
		print(time, rdEng.throt_avg, rdEng.get_eff_fuel_burn_rate() * time_inc)
		rdEng.setThrottle(1, time_inc)
		time += time_inc

	expected_result = 12057.760
	assert almost_equal(fuel_used, expected_result, 0.0000000001)


def main():
	test_fuel_used_in_startup()


if __name__ == '__main__':
	main()
