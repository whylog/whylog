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

	def reverse_from_offset(self, offset, buf_size=8192):
		"""
		a generator that returns the lines of a file in reverse order
		beginning with the specified offset
		"""
		with open(self.open_path) as fh:
			truncated = None
			fh.seek(offset)
			reverse_offset = 0
			total_size = remaining_size = fh.tell()
			start_line_suffix = fh.readline()
			while remaining_size > 0:
				reverse_offset = min(total_size, reverse_offset + buf_size)
				fh.seek(total_size-reverse_offset, 0)
				buffer = fh.read(min(remaining_size, buf_size))
				lines = buffer.split('\n')
				if remaining_size == total_size:
					lines[-1] += start_line_suffix.strip('\n')
				remaining_size -= buf_size
				if truncated is not None:
					if buffer[-1] is not '\n':
						lines[-1] += truncated
					else:
						yield truncated
				truncated = lines[0]
				for index in xrange(len(lines) - 1, 0, -1):
					if len(lines[index]):
						yield lines[index]
			yield truncated
		
	def get_cause(self, vim_line):
		pass
