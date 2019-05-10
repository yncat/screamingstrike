# -*- coding: utf-8 -*-
# Screaming Strike highscore handling.
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains HsStorage class."""
import pickle
import gameModes

class HsStorage(object):
	"""This object stores the highest scores for each mode."""
	def __init__(self):
		self.scores={}

	def initialize(self,filename):
		"""Initializes the storage with the given filename. If this method fails to load the specified file, highscores are reset to zero.

		:param filename, File name to load.
		"""

		try:
			f=open(filename,"rb")
		except IOError:
			self.reset()
			return
		#end except
		try:
			self.scores=pickle.load(f)
		except pickle.PickleError:
			self.reset()
			return
		#end except
	#end initialize

	def reset(self, mode=""):
		"""Resets all high scores. if mode is specified, resets the specified mode only.

		:param mode: Mode to reset high score(empty=all).
		:type mode: str
		"""
		if mode!="":
			self.scores[mode]=0
			return
		#end specific reset
		self.scores={}
	#end reset

	def get(self,mode):
		"""Retrieves the highest score of the specified mode.

		:param mode: Mode to retrieve.
		:type mode: str
		:rtype: int
		"""
		try:
			r=self.scores[mode]
		except KeyError:
			r=0
		#end except
		return r

	def set(self,mode,score):
		"""Sets/updates the highest score of the specified mode.

		:param mode: Mode to set.
		:type mode: str
		:param score: New high score.
		:type score: int
		"""
		self.scores[mode]=score
	#end set

	def save(self,filename):
		"""Saves the high score table to a file. If IO error occurs, saving is skipped.

		:param filename: File name to save.
		:type filename: str
		"""
		try:
			f=open(filename,"wb")
		except IOError:
			return
		#end except
		pickle.dump(self.scores,f)
		f.close()
	#end save