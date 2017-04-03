import unittest

from rocket import main


# test cases adapted from `x-common//canonical-data.json` @ version: 1.0.0

class MainTests(unittest.TestCase):
	def test_hello(self):
		self.assertEqual(main.hello(), 'Hello, World!')


if __name__ == '__main__':
	unittest.main()
