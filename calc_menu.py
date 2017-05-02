from util.menu import *
from generalEquations import *
from util.text_interface import *
from libs.rocketEngine import *
from libs.stage import *
from calc import *
import libs.vehicle
import libs.velocity
import numpy as np


menu_data = {
  "title": "Program Launcher", "type": MENU, "subtitle": "Please select an option...",
  "options":[
  	{ "title": "Rocket Sim", "type": COMMAND, "command": "python main.py" },
	{ "title": "Percent Atm", "type": FUNCTION, "function": prompt_PATM },
	{ "title": "Percent Vac", "type": FUNCTION, "function": prompt_vac },
	{ "title": "Big G", "type": FUNCTION, "function": prompt_big_G },
	{ "title": "ADC K", "type": FUNCTION, "function": prompt_ADC },
	{ "title": "Pre-burn", "type": FUNCTION, "function": prompt_preburn },
	{ "title": "Engine Thrust at Alt", "type": FUNCTION, "function": prompt_thrust_at_alt },

  ]
}



# Main program
while True:
	quit = False
	func = processmenu(menu_data)

	curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
	os.system("clear")
	while not quit:
		func()
		ans = raw_input("Again?")
		if ans != "y":
			quit = True
