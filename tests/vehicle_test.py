import unittest

from vehicle import Vehicle as V

HLV = V.Vehicle()
# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold


class VehicleTests(unittest.TestCase):
	pass
	'''
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

	'''


if __name__ == '__main__':
	unittest.main()
