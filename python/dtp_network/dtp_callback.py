# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class DTPCallback:
	@staticmethod
	def create(function):
		def wrapper(*args, **kwargs):
			return function(*args, **kwargs)
		return wrapper
