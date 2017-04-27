import glob
import json
from util.util import *

from query import *

def save_file(this_file):
	file_name = this_file['file_name']
	save_json(this_file, file_name)

def select_and_load_json_file(files):
	n = 1
	for this_file in files:
		file_data = load_json(this_file)
		print("{}) {}".format(n,file_data["friendly_name"]))
		n += 1
	file_num = query_int("Select a file number: ", None, 1, n-1)
	data = load_json(files[file_num-1])
	return data

def get_json_file_data(folder, name, creation_function):
	files = glob.glob("{}/*.json".format(folder))
	if len(files) < 1: #if there are no spec files, you need to create one
		data = creation_function()
	else:
		create_new = query_yes_no("Do you want to create a new {} file? ".format(name), "no")
		if create_new:
			data = creation_function()
		else:
			data = select_and_load_json_file(files)

	pretty_json(data)
	return data

def create_csv(data, fileName):
	with open(fileName, 'w') as outfile:
		outfile.write(data)

def save_csv(data, fileName):
	with open(fileName, 'a') as outfile:
		outfile.write(data)

def make_dir(fileName):
	if not os.path.exists(os.path.dirname(fileName)):
		try:
			os.makedirs(os.path.dirname(fileName))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

def save_json(data, fileName):
	make_dir(fileName)
	with open(fileName+".json", "w") as outfile:
		json.dump(data, outfile)

def load_json(fileName):
	with open(fileName) as data_file:
		return json.load(data_file)
