import unittest

from rocket import generalEquations as ge


# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
  return abs(x-y) < threshold


class GeneralEquationTests(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(ge.helloGE(), 'Hello, World!')
    def test_PATM_at_sea_level(self):
        self.assertEqual(ge.percentOfAtmosphericPressure(0), 1.00)

    def test_PATM_in_vac(self):
        self.assertEqual(ge.percentOfAtmosphericPressure(300000), 0.00)
    def test_PctVac_at_30000(self):
        PctVac = 1 - ge.percentOfAtmosphericPressure(30000)
        assert almost_equal(PctVac, 0.70304, 0.00001)

    def test_pythag(self):
        self.assertEqual(ge.pythag(3,4),5)

    def test_pythag(self):
        assert almost_equal(ge.pythag(7.1, 4.3), 8.3006)


if __name__ == '__main__':
    unittest.main()
