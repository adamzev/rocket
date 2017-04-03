import unittest

from rocket import rocketEngine as eng

rdData = 	{
"name": "RD-171",
"thrust_sl"  : 1632000.0,
"thrust_vac" : 1777000.0,
"throt" : 1.0,
"engine_count" : 1.0,
"specImp_sl" : 309.68,
"specImp_vac" : 337.19
}

ssData = 	{
		"name": "SSME",
		"thrust_sl"  : 418130.0,
		"thrust_vac" : 512410.0,
		"throt" : 0.95,
		"engine_count" : 1.0,
		"specImp_sl" : 370.35,
		"specImp_vac" : 453.86
	}

rdEng = eng.RocketEngine(rdData)
ssEng = eng.RocketEngine(ssData)
# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold


class EngineTests(unittest.TestCase):
	def test_thrust_RD_sea_level(self):
		rdEng.setThrottle(1)
		self.assertEqual(rdEng.thrustAtAlt(0), 1632000)

	def test_thrust_RD_30000(self):
		rdEng.setThrottle(1)
		assert almost_equal(rdEng.thrustAtAlt(30000), 1733940.707, 0.001)

	def test_thrust_SS_sea_level(self):
		ssEng.setThrottle(0.95)
		assert almost_equal(ssEng.thrustAtAlt(0), 397223.5, 0.001)

	def test_thrust_SS_12000(self):
		ssEng.setThrottle(0.95)
		assert almost_equal(ssEng.thrustAtAlt(12000), 429827.1905, 0.001)



if __name__ == '__main__':
	unittest.main()
