import os
import curses

import util.menu as menu
import calc


menu_data = {
	"title": "Program Launcher", "type": menu.MENU, "subtitle": "Please select an option...",
	"options":[
		{"title": "Rocket Sim", "type": menu.COMMAND, "command": "python main.py"},
		{"title": "Percent Atm", "type": menu.FUNCTION, "function": calc.prompt_PATM},
		{"title": "Percent Vac", "type": menu.FUNCTION, "function": calc.prompt_vac},
		{"title": "Big G", "type": menu.FUNCTION, "function": calc.prompt_big_G},
		{"title": "ADC K", "type": menu.FUNCTION, "function": calc.prompt_ADC},
		{"title": "Pre-burn", "type": menu.FUNCTION, "function": calc.prompt_preburn},
		{"title": "Engine Thrust at Alt", "type": menu.FUNCTION, "function": calc.prompt_thrust_at_alt},

  ]
}



# Main program
while True:
	func = menu.processmenu(menu_data)

	curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
	os.system("clear")
	while True:
		func()
		ans = raw_input("Again?")
		if ans != "y":
			break
