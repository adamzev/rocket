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
	RD171M.burnFuel(time_inc)
	'''
		calculate how much fuel the engine uses during its power down sequence
		if the fuel remaining is <= fuel used in power down begin shutdown
	'''
	print ("Time {}".format(time))
	print ("Fuel Used = {} Throt = {}".format(RD171M.fuelUsed, current(RD171M.throt)))
