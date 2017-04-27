import json
import sys
import os
import re
import glob
from colorama import init, Fore, Back, Style
init()

def remove_non_alphanumeric(your_string):
	return re.sub(r'\W+', '', your_string)

def stopPrinting(my_loud_function):
	sys.stdout = open(os.devnull, "w")
	my_loud_function()
	sys.stdout = sys.__stdout__

def printTable(table_data, cols):
	maxWidth = 170
	maxCellWidth = maxWidth / cols
	for row in table_data:
		rowString = "{: >"+str(maxCellWidth)+"}"
		rowString = rowString * len(row)
		print(rowString.format(*row))


def pretty_json(parsed_json):
	print json.dumps(parsed_json, indent=4, sort_keys=True)
def current(myArray):
	return myArray[-1]


def prev(myArray):
	''' Gets the previous value if it exists, otherwise returns the current value

	'''
	try:
		return myArray[-2]
	except IndexError:
		return myArray[-1]

def get_value(myArray, when="current"):
	if when == "current":
		return current(myArray)
	else:
		return prev(myArray)


def create_csv(data, fileName):
	with open(fileName, 'w') as outfile:
		outfile.write(data)


def save_csv(data, fileName):
	with open(fileName, 'a') as outfile:
		outfile.write(data)

def save_json(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile)

def load_json(fileName):
	with open(fileName) as data_file:
		return json.load(data_file)

def query_multiple(queries):
	results = {}
	for name in queries:
		if queries['type'] == "float":
			results[name] = query_float(queries[name]['prompt'])
		elif queries['type'] == "bool":
			results[name] = query_float(queries[name]['prompt'])
		elif queries['type'] == "int":
			results[name] = query_int(queries[name]['prompt'])
		else:
			results[name] = input(queries[name]['prompt'])

def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".

	From: http://code.activestate.com/recipes/577058/
	"""
	valid = {"yes": True, "y": True, "ye": True,
			 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "
							 "(or 'y' or 'n').\n")


def is_float(the_string):
	try:
		x = float(the_string)
		return True
	except ValueError:
		return False

def is_int(the_string):
	try:
		x = int(the_string)
		return True
	except ValueError:
		return False


def query_float(question, default=None):
	"""Ask a question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be any float or None

	The "answer" return value is a float value.
	"""

	while True:
		sys.stdout.write(question)
		choice = raw_input()
		if default is not None and choice == '':
			return default
		elif is_float(choice):
			return float(choice)
		else:
			sys.stdout.write("Please respond with a valid number.\n")

def query_int(question, default=None, min_num=None, max_num=None):
	"""Ask a question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be any float or None

	The "answer" return value is a float value.
	"""
	valid = False
	while True:
		sys.stdout.write(question)
		choice = raw_input()
		if default is not None and choice == '':
			return default
		if is_int(choice):
			choice = int(choice)
			if min_num is None and max_num is None:
				return choice
			elif min_num is None and choice <= max_num:
				return choice
			elif  max_num is None and choice >= min_num:
				return choice
			elif min_num <= choice <= max_num:
				return choice
		sys.stdout.write("Please respond with a valid number.\n")


def query_min_max(question, min_num=0.0, max_num=1.0):
	"""Ask a question via raw_input() where "min", "max", "off" or a number in a range are valid and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".

	From: http://code.activestate.com/recipes/577058/
	"""
	prompt = " [min/max/off/{}-{}] ".format(min_num, max_num)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if choice == 'min' or choice == 'max' or choice == 'off':
			return choice
		elif is_float(choice) and min_num <= float(choice) <= max_num:
			return float(choice)
		else:
			sys.stdout.write("Please respond with 'min', 'max', 'off' or a number between {} and {}. \n".format(min_num, max_num))

def real_quadradric(a , b, c):
	disc = b**2 - 4 * a * c
	assert disc >= 0

	x1 = (-b + disc**0.5)/(2.0*a)
	x2 = (-b - disc**0.5)/(2.0*a)

''' SET BREAKPOINTS BY '''
def break_point():
	import pdb; pdb.set_trace()
