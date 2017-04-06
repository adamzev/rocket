import unittest

from rocket import generalEquations as ge


# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold


class GeneralEquationTests(unittest.TestCase):
	def test_PATM_at_sea_level(self):
		self.assertEqual(ge.percentOfAtmosphericPressure(0), 1.00)

	def test_PATM_in_vac(self):
		self.assertEqual(ge.percentOfAtmosphericPressure(300000), 0.00)
	def test_PctVac_at_30000(self):
		PctVac = 1 - ge.percentOfAtmosphericPressure(30000)
		assert almost_equal(PctVac, 0.70304, 0.00001)

	def test_pythag(self):
		self.assertEqual(ge.pythag(3,4),5)

	def test_pythag_dec(self):
		assert almost_equal(ge.pythag(7.1, 4.3), 8.3006)

	def test_avg(self):
		self.assertEqual(ge.average(2,4,12), 6)

	def test_avg_dec(self):
		assert almost_equal(ge.average(2.4, 4.3, 5.2, 9.8), 5.425)

	def test_orbitalV(self):
		assert almost_equal(ge.orbitalVelocity(0), 17683.9567, 0.001)

	def test_orbitalV_3000(self):
		assert almost_equal(ge.orbitalVelocity(3000), 17682.6878, 0.001)

	def test_orbitalV_12000(self):
		assert almost_equal(ge.orbitalVelocity(12000), 17678.8829, 0.001)

	def test_orbitalV_25000(self):
		assert almost_equal(ge.orbitalVelocity(25000), 17673.3911, 0.001)
	def test_mphToFps(self):
		assert almost_equal(ge.mphToFps(1), 1.46667)
	def test_mphToFps_large(self):
		assert almost_equal(ge.mphToFps(17673.3911), 25920.9736)
	def test_bigG(self):
		orbitalV = ge.orbitalVelocity(407030)
		horizontalVelocity = 11598.89186
		assert almost_equal(ge.bigG(horizontalVelocity, orbitalV), .561418429, 0.00001)

if __name__ == '__main__':
	unittest.main()
