# -*- coding: utf-8 -*-
# Screaming Strike score posting adapters
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
"""This module contains the base class of adapters for score posting. You need to make your own adapter by inheriting this class. You may add your extended class in this module, but distributing the modified module is not recommended."""
import gameResult

# return values of post method
RET_UNAVAILABLE = 0
RET_CONNECTION_ERROR = -1
RET_TOO_LOW = -2


class AdapterBase(object):
    """Inherit this class and override the post methods to make your own adapter."""

    def __init__(self):
        self.lastError = None

    def post(self, name, result):
        """Posts the given game result using this adapter. This base class does nothing and returns RET_UNAVAILABLE.
        You must return the position on the scoreboard (>0) on success, or RET_CONNECTION_ERROR when connection error occured.

        :param name: Player name.
        :type name: str
        :param result: Game result instance which will be posted.
        :type result: gameResult.GameResult

        :rtype: int
        """
        return RET_UNAVAILABLE

    def getLastError(self):
        """Retrieves the last error.

        :rtype: str
        """
        return self.lastError
