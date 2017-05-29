import unittest
import random
import string

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from rocket.libs.query import Query as q
def rand_input(_question):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def specific_input(input_to_return):
	return input_to_return


def input_generator(inputs_to_return):
	for input_value in inputs_to_return:
		yield input_value

class QueryTests(unittest.TestCase):
	def test_query_string(self):
		my_inputs = ["here", "are", "some", "s", "hort" "andlongStrings to teSt"]
		for my_input in my_inputs:
			q.change_input_func(lambda x, my_in=my_input: specific_input(my_in))
			result = q.query_string("Test? ", None)
			assert my_input == result
	def test_query_random_string(self):
		q.change_input_func(rand_input)
		for i in range (1000):
			result = q.query_string("Test? ", None)
			assert isinstance(result, str)

	def test_query_string_default_input(self):
		q.change_input_func(lambda x: specific_input(""))
		default = "pizza"
		result = q.query_string("Test? ", default)
		assert result == default

	def test_query_int(self):
		''' test only integer values are returned '''
		gen = input_generator(["x", "pizza", "5.3", "12"])
		q.change_input_func(lambda: next(gen))
		result = q.query_int("Test? ", None)
		assert result == 12

	def test_query_int_with_commas(self):
		''' test only integer values are returned '''
		gen = input_generator(["x", "pizza", "5.3", "12,305,127"])
		q.change_input_func(lambda: next(gen))
		result = q.query_int("Test? ", None)
		assert result == 12305127

	def test_query_int_no_good_input(self):
		''' test only integer values are returned '''
		gen = input_generator(["x", "pizza", "5.3", "a", "+"])

		q.change_input_func(lambda: next(gen))
		with self.assertRaises(StopIteration):
			q.query_int("Test? ", None)



if __name__ == '__main__':
	unittest.main()
