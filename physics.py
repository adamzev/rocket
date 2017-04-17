from generalEquations import *
from util import *


class Physics:
	def __init__(self, params):
		self._A_vert_eff = 0.0
		self._A_vert = 0.0
		self._A_horiz = 0.0
		self._A_total = 0.0
		self._A_total_eff = 0.0
		self._V_vert = 0.0
		self._V_vert_eff = 0.0
		self._V_vert = 0.0
		self._V_vert_inc = 0.0
		self._V_horiz_mph = 912.67
		self._V_horiz_mph_inc = 0.0
		self._V_total = 0.0
		self._A_vert_eff_prev = 0.0
		self._A_vert_prev = 0.0
		self._A_horiz_prev = 0.0
		self._A_total_prev = 0.0
		self._A_total_eff_prev = 0.0
		self._V_vert_prev = 0.0
		self._V_vert_eff_prev = 0.0
		self._V_vert_prev = 0.0
		self._V_vert_inc_prev = 0.0
		self._V_horiz_mph_prev = 912.67
		self._V_horiz_mph_inc_prev = 0.0
		self._V_total_prev = 0.0
