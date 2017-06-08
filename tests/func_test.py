import unittest

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import rocket.util.func as func


class FuncTests(unittest.TestCase):
	def test_linear_estimate_halfway(self):
		result = func.linear_estimate(13.5, [12, 15], [100, 200])
		assert func.almost_equal(result, 150)

	def test_linear_estimate_122(self):
		result = func.linear_estimate(12.2, [12, 15], [100, 200])
		assert func.almost_equal(result, 106.66666667)

	def test_linear_estimate_12(self):
		result = func.linear_estimate(12, [12, 15], [100, 200])
		assert func.almost_equal(result, 100)

	def test_linear_estimate_15(self):
		result = func.linear_estimate(15, [12, 15], [100, 200])
		assert func.almost_equal(result, 200)

	def test_linear_estimate_more_values(self):
		result = func.linear_estimate(19.3, [12, 13, 18, 20], [12.5, 14.3, 17.2, 81.9])
		assert func.almost_equal(result, 59.255)

	def test_linear_estimate_last_of_more_values(self):
		result = func.linear_estimate(20.000001, [12, 13, 18, 20], [12.5, 14.3, 17.2, 81.9])
		assert func.almost_equal(result, 81.9)

if __name__ == '__main__':
	unittest.main()