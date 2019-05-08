# -*- coding: utf-8 -*-
# Screaming Strike score posting adapters
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains the base class of adapters for score posting. You need to make your own adapter by inheriting this class. You may add your extended class in this module, but distributing the modified module is not recommended."""
import gameResult

#return values of post method
RET_OK=1
RET_UNAVAILABLE=0
RET_CONNECTION_ERROR=-1

class AdapterBase(object):
	"""Inherit this class and override all methods to make your own adapter."""
	def post(self,result):
		"""Posts the given game result using this adapter. This base class does nothing and returns RET_UNAVAILABLE.
		You must return RET_OK on success or RET_CONNECTION_ERROR when connection error occured.

		:param result: Game result instance which will be posted.
		:type result: gameResult.GameResult

		:rtype: int
		"""
		return ERROR_UNAVAILABLE

