# -*- coding: utf-8 -*-
# Screaming Strike game results class
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains GameResult class."""

class GameResult:
	"""This class stores a gameplay's result. """
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,field):
		"""
		Populates the game results from the given field instance.

		:param field: Field instance from which the game results are loaded.
		:type field: gameField.GameField
		"""
		self.score=field.player.score
		self.hitPercentage=field.player.hitPercentage
		self.hits=field.player.hits
		self.punches=field.player.punches
		self.level=field.level
		self.mode=field.modeHandler.getName()
