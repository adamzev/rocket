from generalEquations import *
from util import *
class TwoD(object):
	def __init__(self, horiz, vert, total = None):
		self._horiz = horiz
		self._vert = vert
		self._total = total
		self.update()

	@property
	def horiz(self):
		return self._horiz

	@horiz.setter
	def horiz(self, value):
		self._horiz = value
		self.update()

	@property
	def vert(self):
		return self._vert

	@vert.setter
	def vert(self, value):
		self._vert = value
		self.update()

	@property
	def total(self):
		return self._total

	@total.setter
	def total(self, value):
		self._total = value
		self.update()

	def update(self):
		if self.total is None:
			self._total = pythag(self.horiz, self.vert, None)

		elif self.horiz is None:
			self._horiz = pythag(None, self.vert, self.total)

		elif self.vert is None:
			self._vert = pythag(self.horiz, None, self.total)
