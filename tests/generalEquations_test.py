import unittest

from rocket import generalEquations as ge


# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold

def accurateToPercent(result, expected,threshold=0.9999):
	if expected == 0:
		return result == expected
	return (1 - abs(result-expected)/expected) > threshold

class GeneralEquationTests(unittest.TestCase):
	def test_PATM_at_sea_level(self):
		self.assertEqual(ge.percentOfAtmosphericPressure(0), 1.00)

	def test_PATM_at_sea_level_to_36089ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(14000), 0.5874546564, 0.0000000001)

	def test_PATM_at_36089_to_65617_ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(40000), 0.1850849065, 0.0000000001)

	def test_PATM_at_65617_to_104987_ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(80000), 0.0272535655, 0.0000000001)

	def test_PATM_at_104987_to_154199_ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(120000), 0.0044045444, 0.0000000001)

	def test_PATM_at_154199_to_167323_ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(160000), 0.0008756462207, 0.0000000001)

	def test_PATM_at_167323_to_232940_ft(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(180000), 0.000401591024, 0.0000000001)

	def test_PATM_at_232940_to_278386_KM(self):
		assert almost_equal(ge.percentOfAtmosphericPressure(250000), 0.00001671655006, 0.0000000001)

	def test_PATM_in_vac(self):
		self.assertEqual(ge.percentOfAtmosphericPressure(300000), 0.00)


	def test_PctVac_at_30000(self):
		PctVac = ge.percentOfVac(30000)
		assert almost_equal(PctVac, 0.70304, 0.00001)
		assert accurateToPercent(PctVac, 0.70304)

	def test_pythag(self):
		self.assertEqual(ge.pythag(3, 4), 5)

	def test_pythag_missing_a(self):
		self.assertEqual(ge.pythag(None, 4, 5), 3)

	def test_pythag_missing_b(self):
		self.assertEqual(ge.pythag(3, None, 5), 4)

	def test_pythag_missing_a_and_c(self):
		self.assertEqual(ge.pythag(None, 4), None)

	def test_pythag_dec(self):
		assert almost_equal(ge.pythag(7.1, 4.3), 8.3006)

	def test_avg(self):
		self.assertEqual(ge.average(2,4,12), 6)

	def test_avg_dec(self):
		assert almost_equal(ge.average(2.4, 4.3, 5.2, 9.8), 5.425)


	def test_mphToFps(self):
		assert almost_equal(ge.mphToFps(1), 1.46667)

	def test_mphToFps_large(self):
		assert almost_equal(ge.mphToFps(17673.3911), 25920.9736)

	def test_fps_to_mph(self):
		assert almost_equal(ge.fpsToMph(1.46667), 1)

	def test_fps_to_mph_large(self):
		assert almost_equal(ge.fpsToMph(25920.9736), 17673.3911)

	def test_bigG(self):
		orbitalV = ge.orbitalVelocity(407030)
		horizontalVelocity = 11598.89186
		assert almost_equal(ge.bigG(horizontalVelocity, orbitalV), .561418429, 0.00001)

	def test_bigG_no_negatives(self):
		orbitalV = ge.orbitalVelocity(4070300)
		horizontalVelocity = 115980.89186
		assert almost_equal(ge.bigG(horizontalVelocity, orbitalV), 0.0, 0.00001)

	def test_myround(self):
		assert ge.myround(472, 150) == 450

	def test_altitude(self):
		alt_prev = 5345
		V_vert_prev = 438.7465593
		V_vert_inc = 51.4
		time_inc = 3
		assert almost_equal(ge.altitude(alt_prev, V_vert_prev, V_vert_inc, time_inc), 6738, 1)

	def test_ADC(self):
		airSpeed = 437.057
		alt = 6738
		K = 1.832
		result = 0.272734938
		assert almost_equal(ge.ADC(airSpeed, alt, K), result, 0.0001)
		assert accurateToPercent(ge.ADC(airSpeed, alt, K), result)

	def test_ADC_13687ft(self):
		airSpeed = 594.7295
		alt = 13687
		K = 2.386
		result = 0.5019203
		assert almost_equal(ge.ADC(airSpeed, alt, K), result, 0.001)
		assert accurateToPercent(ge.ADC(airSpeed, alt, K), result, 0.999)

	def test_ADC_89335ft(self):
		airSpeed = 2183.4086
		alt = 89335
		K = 2.244
		result = 0.1888547
		assert almost_equal(ge.ADC(airSpeed, alt, K), result, 0.001)
		assert accurateToPercent(ge.ADC(airSpeed, alt, K), result, 0.9999999)

if __name__ == '__main__':
	unittest.main()
