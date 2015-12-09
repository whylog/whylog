from abc import ABCMeta, abstractmethod

class Searcher(object):
	__metaclass__ = ABCMeta


class IndexSearcher(Searcher):
	pass

class DataBaseSearcher(Searcher):
	pass

class BacktrackSearcher(Searcher):

	def __init__(self, file_path):
		self._file_path = file_path
