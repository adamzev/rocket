import unittest

import rocket.libs.eventsManager as eventMan

# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold

def accurateToPercent(result, expected,threshold=0.9999):
	if expected == 0:
		return result == expected
	return (1 - abs(result-expected)/expected) > threshold

class EventManTests(unittest.TestCase):
	''' load a generic rocket

		test that after querying for something that it appears in the event property of eventManager
		test that if given some invalid input, it keeps querying until valid input is given

	'''

if __name__ == '__main__':
	unittest.main()
