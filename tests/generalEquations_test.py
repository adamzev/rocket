import unittest

from rocket import generalEquations as ge


# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
  return abs(x-y) < threshold


class MainTests(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(ge.helloGE(), 'Hello, World!')

	def test_PATM_at_sea_level(self):
		self.assertEqual(ge.percentOfAtmosphericPressure(0), 0.00)

	def test_PATM_in_vac(self):

		self.assertEqual(ge.percentOfAtmosphericPressure(300000), 5.00)
	def test_PctVac_at_30000(self):
		PctVac = 1 - ge.percentOfAtmosphericPressure(30000)
		assert almost_equal(PctVac, 1.70304)


if __name__ == '__main__':
    unittest.main()
