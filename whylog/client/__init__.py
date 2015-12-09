from abc import ABCMeta, abstractmethod
import os

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
		self.rulesbase = rulesbase
		self.open_path = open_path
		
	def get_cause(self, offset, vim_line):
		pass
