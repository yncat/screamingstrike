# -*- coding: utf-8 -*-
# Screaming Strike statisticks manager
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains StatsStorage class, which can store high scores and other statisticks about the game."""
import pickle
import gameModes

class StatsStorage(object):
	"""This object stores the game's statistics."""
	def __init__(self):
		self.items={}

	def initialize(self,filename):
		"""Initializes the storage with the given filename. If this method fails to load the specified file, everything is reset to zero.

		:param filename, File name to load.
		"""

		try:
			f=open(filename,"rb")
		except IOError:
			self.resetAll()
			return
		#end except
		try:
			self.items=pickle.load(f)
		except (pickle.PickleError, EOFError):
			self.resetAll()
			return
		#end except
	#end initialize

	def resetAll(self):
		"""Resets everything in this storage.
		"""
		self.items={}
	#end resetAll

	def resetHighscores(self):
		"""Resets highscores only."""
		for mode in gameModes.ALL_MODES_STR:
			self.items["hs_"+mode]=0
		#end for
	#end resetHighscores

	def get(self,key):
		"""Retrieves the specified value.

		:param key: Key to retrieve.
		:type key: str
		:rtype: int
		"""
		try:
			r=self.items[key]
		except KeyError:
			r=0
		#end except
		return r

	def set(self,key,value):
		"""Sets/updates the specified value.

		:param key: Key to set.
		:type key: str
		:param value: New value.
		:type value: int
		"""
		self.items[key]=value
	#end set

	def inclement(self,key, unit=1):
		"""Inclements the specified value by unit. If the key doesn't exist, create one.

		:param unit: Unit. Default is 1.
		:type unit: int
		"""
		self.checkKey(key)
		self.items[key]=self.items[key]+unit
	#end inclement

	def declement(self,key, unit=1):
		"""Declements the specified value by unit. If the key doesn't exist, does nothing.

		:param unit: Unit. Default is 1.
		:type unit: int
		"""
		self.keyCheck(key)
		self.items[key]=self.items[key]-unit
	#end inclement

	def checkKey(self,key):
		"""Checks the specified key. If it doesn't exist, create a new one with 0.

		:param key: Key to check.
		:type key: str
		"""
		if not key in self.items: self.items[key]=0

	def save(self,filename):
		"""Saves the storage to a file. If IO error occurs, saving is skipped.

		:param filename: File name to save.
		:type filename: str
		"""
		try:
			f=open(filename,"wb")
		except IOError:
			return
		#end except
		pickle.dump(self.items,f)
		f.close()
	#end save