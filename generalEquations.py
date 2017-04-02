import math

ACCEL_OF_GRAVITY = 32.17405

def percentOfAtmosphericPressure(alt):
  #where sea level PATM = 1.00 and vacuum PATM = 0.00; altitude given in feet

  #1
  if alt <= 36089:
    return (1 - (alt/145442.0)) ** 5.255877122
  #2
  elif alt<= 65617: #(11 km to 20 km)
    # where 'math.exp' is exponential function 'e' raised to the 'x' power
    return 0.223361 * math.exp((36089- alt)/20806.0)
  #3
  elif alt <= 104987: #(20 km to 32 km)
    return (0.988626 + (alt / 652600.0)) ** (-34.16319)
  #4
  elif alt <= 154199: #(32 km to 47 km)
    return (0.898309 + (alt / 181373.0)) ** (-12.20114)
  #5
  elif alt <= 167323: #(47 km to 51 km)
    return 0.00109456 * math.exp((alt - 154200)/-25922.0)
  #6
  elif alt <= 232940: #(51 km to 71 km)
    return (0.838263 - (alt / 577922.0)) ** (12.20114)
  #7
  elif alt <= 278386: #(71 km to 84.852 km)
    return (0.917131 - (alt / 637919.0)) ** (17.08160)
  #8
  else: #for alt> 84.852
    return 0.00



'''
Orbital Velocity (OV) is that horizontal velocity needed to counteract Earth's gravity at a given altitude

OV decreases as you increase your radial distance from the center of the Earth, i.e. increase altitude.

Alt in feet

'''
def helloGE():
    return "Hello, World!"

def orbitalVelocity(alt):
  return 17683.9567 * ( ( 1.0 / ( 1+ ( alt / 20902230.99 ) ) )** 0.5 )

def average(*args):
	return sum(args)/float(len(args))


def pythag(a, b):
	return math.sqrt(a**2 + b**2)

'''
______________________________________________________________________

"G" is downward (vertical) acceleration: Earth's gravity minus centrifugal force caused by horizontal velocity (V H )
_________________________________________________________________________
'''

def gravity(horizontalVelocity, orbitalVelocity):
  return 1 - ( (horizontalVelocity / orbitalVelocity)**2 )
