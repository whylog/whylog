from abc import ABCMeta, abstractmethod

from whylog.rulesbase import WhylogBase


class AbstractClient(object):

	__metaclass__ = ABCMeta

	@abstractmethod
	def get_cause(self):
		pass


class WhylogClient(AbstractClient):
	"""
	first naive client implementation
	"""

	def __init__(self, rulesbase, open_path):
		self._rulesbase = rulesbase
		self._open_path = open_path

	def get_cause(self, vim_line):
		pass
