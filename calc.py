from menu import *
from generalEquations import *

def promptPATM():
	print "Percent of Atm Pressure Calculator"
	alt = float(raw_input("Alt? "))
	print percentOfAtmosphericPressure(alt)

def promptVac():
	print "Percent of Atm Vac Calculator"
	alt = float(raw_input("Alt? "))
	print percentOfVac(alt)

menu_data = {
  'title': "Program Launcher", 'type': MENU, 'subtitle': "Please select an option...",
  'options':[
  	{ 'title': "Rocket Sim", 'type': COMMAND, 'command': 'python main.py' },
	{ 'title': "Percent Atm", 'type': FUNCTION, 'function': promptPATM },
	{ 'title': "Percent Vac", 'type': FUNCTION, 'function': promptVac },

	{ 'title': "Dosbox Games", 'type': MENU, 'subtitle': "Please select an option...",
	'options': [
	  { 'title': "Midnight Rescue", 'type': COMMAND, 'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SSR/SSR.EXE -exit' },
	  { 'title': "Outnumbered", 'type': COMMAND, 'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SSO/SSO.EXE -exit' },
	  { 'title': "Treasure Mountain", 'type': COMMAND, 'command': 'dosbox /media/samba/Apps/dosbox/doswin/games/SST/SST.EXE -exit' },
	]
	},
	{ 'title': "Pianobar", 'type': COMMAND, 'command': 'clear && pianobar' },
	{ 'title': "Windows 3.1", 'type': COMMAND, 'command': 'dosbox /media/samba/Apps/dosbox/doswin/WINDOWS/WIN.COM -conf /home/pi/scripts/dosbox2.conf -exit' },
	{ 'title': "Reboot", 'type': MENU, 'subtitle': "Select Yes to Reboot",
	'options': [
	  {'title': "NO", 'type': EXITMENU, },
	  {'title': "", 'type': COMMAND, 'command': '' },
	  {'title': "", 'type': COMMAND, 'command': '' },
	  {'title': "", 'type': COMMAND, 'command': '' },
	  {'title': "YES", 'type': COMMAND, 'command': 'sudo shutdown -r -time now' },
	  {'title': "", 'type': COMMAND, 'command': '' },
	  {'title': "", 'type': COMMAND, 'command': '' },
	  {'title': "", 'type': COMMAND, 'command': '' },
	]
	},

  ]
}



# Main program
while True:
	quit = False
	func = processmenu(menu_data)

	curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
	os.system('clear')
	func()
	raw_input("Continue?")
