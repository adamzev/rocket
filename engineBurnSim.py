from rocketEngine import *
from util import *

RD171M_data = {
		"name": "RD-171M",
		"thrust_sl"  : 1632000.0,
		"thrust_vac" : 1777000.0,
		"min_throt" : 0.56,
		"max_throt" : 1.0,
		"lbm_dry" : 20503,
		"fuel" : 5932224.827,
		"residual" : 0.015,
		"throt_rate_of_change_limit" : 0.15,
		"engine_count" : 8.0,
		"burn_rate" : 5270.0,
	}
RD171M = RocketEngine(RD171M_data)

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

SRM = RocketEngine(SRM_data)

SRM.setThrottleOverride(SRM.max_throt)
SRM.setThrottleOverride(SRM.max_throt)

def simSRM():
	SRM.set_assigned_thrust(3600000.0)
	low_on_fuel = False
	time = 0
	time_inc = 1
	alts = [50, 58.71, 86.54, 136.93, 431.09, 928.82, 1617.67, 3546.94]
	times = [0, 1, 2, 3, 6, 9, 12, 15, 18]
	# LOW ON FUEL NOT YET IMPLMENTED
	for i in range(len(times)):
		time = times[i]
		time_inc = times[i+1]-times[i]
		alt = alts[i]

		SRM.burn_fuel(time_inc, alt)
		'''
			calculate how much fuel the engine uses during its power down sequence
			if the fuel remaining is <= fuel used in power down begin shutdown
		'''
		print ("Time {}".format(time))
		print ("Fuel Used = {} Throt = {}".format(SRM.get_fuelUsed(), current(SRM.throt)))
simSRM()

def simRD171M():
	RD171M.setThrottleOverride(RD171M.min_throt)
	RD171M.setThrottleOverride(RD171M.min_throt)
	low_on_fuel = False
	time = 0
	time_inc = 0.1

	# LOW ON FUEL NOT YET IMPLMENTED
	while RD171M.getUsableFuelRemaining() >=0:
		time = time + time_inc
		if current(RD171M.throt) < RD171M.max_throt and not low_on_fuel:
			RD171M.setThrottle(RD171M.max_throt, time_inc)
		RD171M.burn_fuel(time_inc)
		'''
			calculate how much fuel the engine uses during its power down sequence
			if the fuel remaining is <= fuel used in power down begin shutdown
		'''
		print ("Time {}".format(time))
		print ("Fuel Used = {} Throt = {}".format(RD171M.fuelUsed, current(RD171M.throt)))
