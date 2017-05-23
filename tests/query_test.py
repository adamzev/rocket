import unittest
import random
import string

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import rocket.libs.query as q
def rand_input(_question):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def specific_input(input_to_return):
    return input_to_return

class QueryTests(unittest.TestCase):
	def test_query_string(self):
		my_inputs = ["here", "are", "some", "s", "hort" "andlongStrings to teSt"]
		for my_input in my_inputs:
			result = q.query_string("Test? ", None, lambda x, my_in=my_input: specific_input(my_in))
			assert my_input == result
	def test_query_random_string(self):
		for i in range (1000):
			result = q.query_string("Test? ", None, rand_input)
			assert isinstance(result, str)

	def test_query_string_default_input(self):
		default = "pizza"
		result = q.query_string("Test? ", default, lambda x: specific_input(""))
		assert result == default


if __name__ == '__main__':
	unittest.main()
