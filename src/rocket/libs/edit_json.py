""" edit an existing json file """

import libs.fileManager as fileMan
from libs.query import Query as q


def edit_list(list_to_edit):
	new_list = []
	for value in list_to_edit:
		print(value)
		edit_it = q.query_yes_no("Modify the value? ", "no")
		if edit_it:
			new_list.append(edit_by_type(value))
		else:
			new_list.append(value)
	return new_list


def modify_data(value):
	return q.query_unknown_type("Enter a new value:", value)


def edit_by_type(value):
	if isinstance(value, tuple):
		raise ValueError("Replacing tuples is not implemented")
	if isinstance(value, list):
		return edit_list(value)
	elif isinstance(value, dict):
		return edit_dict_values(value)
	else:
		return q.query_unknown_type("Enter a new value:", value)

def edit_dict_values(json_data):
	''' edit the value of json_data '''
	for key, value in json_data.items():
		print (key + " : " + str(value))
		edit_it = q.query_yes_no("Modify the value? ", "no")
		if edit_it:
			json_data[key] = edit_by_type(value)

	return json_data


def load_and_edit_file(file_name):
	json_data = fileMan.load_json(file_name)
	edit_dict_values(json_data)
	save = q.query_yes_no("Do you want to save your changes? ", "yes")
	if save:
		fileMan.save_file(json_data)


# display the file
# ask if we are adding to or editting the file
# if editing:
# print all keys
# if value is object call recursively
# query if it should be modified
# insert the modification
# save the file

# if adding select from list of things you can add
