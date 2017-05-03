class EventManager:
	available_events = [
		{
			"name" :"Set Throttle Target",
			"description": "Set the target throttle for all engines (regardless of stage) that match a name",
			"data_needed": [
				{
					"order" : 1,
					"field" : "engine_name",
					"type" : "string_from_list"

				},
				{
					"order" : 2,
					"field" : "target",
					"type" : "min_max_float"
				},
			]
		},
		{
			"name" :"Set Throttle Target By Stage",
			"description": "Set the target throttle for all engines that match a name in a given stage",
			"data_needed": [
				{
					"order" : 1,
					"field" : "engine_name",
					"type" : "string_from_list"
					
				},
				{
					"order" : 2,
					"field" : "stage",
					"type" : "string_from_list"
					
				},
				{
					"order" : 3,
					"field" : "target",
					"type" : "min_max_float"
				},

		},
		{
			"name" :"Change Thrust",
			"description": "Change the thrust of a SRM by a given rate of change "
		},
		{
			"name" :"Adjust Weight",
			"description": "This can be used to correct errors or to jettison parts other than the listed stages"
		},
		{
			"name" :"Adjust Acceleration"",
			"description": "This can be used to correct acceleration errors"
		},
		{
			"name" :"Power Down Thrust",
			"description": "Power down a rocket engine based on thrust. This is only used for solid fueled boosters."
		},
		{
			"name" :"Power Down Thrust",
			"description": "Power down a rocket engine based on thrust. This is only used for solid fueled boosters."
		},

	]
	def __init__(self, rocket):
		self.HLV = rocket
		collect_events = True
		while collect_events:
			event = self.list_availabe_events()
			if not event:
				collect_events = False
			else:
				print event["name"], event["description"]


	def list_availabe_events()
		n = 1
		for event in self.available_events:	
			print("{}) {}".format(n, event["name"]))
				n += 1

		print("{}) Finished entering events".format(n))
		event_num = q.query_int("Select an event number: ", None, 1, n)
		if event_num == n:
			return False
		else:
			return self.available_events[n-1]