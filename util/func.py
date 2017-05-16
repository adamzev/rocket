import json
import sys
import os
import re
import glob
from colorama import init, Fore, Back, Style
init()

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

def getNextKey(my_dict):
	''' returns a key from my dict. Use this function to manually loop through a dict or to access the key of a one key dict'''
	return next(iter(my_dict))

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


def real_quadradric(a , b, c):
	disc = b**2 - 4 * a * c
	assert disc >= 0

	x1 = (-b + disc**0.5)/(2.0*a)
	x2 = (-b - disc**0.5)/(2.0*a)

''' SET BREAKPOINTS BY '''
def break_point():
	import pdb; pdb.set_trace()

def almost_equal(x,y,threshold=0.0001):
	return abs(x-y) < threshold