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

def edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust, ADC_guess = 0.0, ADC_actual = 0.0, ADC_adj = 0.0, A_total_eff = 0.0):
	row1 = "-"*140 + "\n"
	row2 = "{:>46.6f}      {:>6.8f}     G={: <12.8f}\n".format(A_total_eff, ADC_actual, big_G)
	time_string = "{:<6.1f}".format(time)
	time_string = Fore.RED + time_string + Style.RESET_ALL
	row3 = "+{:<12.2f} {:5} WT={:<11.2f}->{:>9.6f}      {:<12.8f}   Vh={:<12.6f} Vas={:<12.3f}     {:<12.6f}-{:<10.8f}\n".format(
		V_vert_inc, time_string, totalWeight, totalA, ADC_adj, V_horiz, V_as, A_v, A_h
	)
	alt_string = "ALT={:<.1f}\'".format(alt)
	row4 = "{:<13.6f} {:<16} T={:<19.4f}  \"{:<.4f}\"\n".format(V_vert, alt_string, thrust, ADC_guess)
	print(row1+row2+row3+row4)

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
def save_json(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile)

def load_json(fileName):
	with open(fileName) as data_file:
		return json.load(data_file)

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
''' SET BREAKPOINTS BY '''
# import pdb; pdb.set_trace()

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
