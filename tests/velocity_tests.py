import unittest

from rocket import generalEquations as ge


class VelocityTests(unittest.TestCase):
	def test_orbitalV(self):
		assert almost_equal(ge.orbitalVelocity(0), 17683.9567, 0.001)
		assert accurateToPercent(ge.orbitalVelocity(0), 17683.9567)

	def test_orbitalV_3000(self):
		assert almost_equal(ge.orbitalVelocity(3000), 17682.6878, 0.001)

	def test_orbitalV_12000(self):
		assert almost_equal(ge.orbitalVelocity(12000), 17678.8829, 0.001)

	def test_orbitalV_25000(self):
		assert almost_equal(ge.orbitalVelocity(25000), 17673.3911, 0.001)
