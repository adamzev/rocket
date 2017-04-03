import argparse
from generalEquations import *

parser = argparse.ArgumentParser(description='Returns percent of atmospheric pressure.')
parser.add_argument('alt', type=float)
parser.add_argument("-v", action="store_true", help="Returns percent vacuum")
args = parser.parse_args()

alt = args.alt
if args.v:
	print 1 - percentOfAtmosphericPressure(alt)
else:
	print percentOfAtmosphericPressure(alt)
