# -*- coding: utf-8 -*-
# Screaming Strike score view adapters
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
"""This module contains the base class of adapters for score viewing. You need to make your own adapter by inheriting this class. You may add your extended class in this module, but distributing the modified module is not recommended."""
import gameModes

# return values of post method
RET_UNAVAILABLE = 0
RET_CONNECTION_ERROR = -1
RET_TOO_LOW = -2


class AdapterBase(object):
    """Inherit this class and override the get methods to make your own adapter."""

    def __init__(self):
        self.lastError = None

    def get(self, mode):
        """Retrieves the score table from the server. This base class does nothing and returns RET_UNAVAILABLE.
        You must use gameModes.ALL_MODES_STR constants for identifying game modes.

        :param mode: Game mode to retrieve.
        :type name: str

        :rtype: list
        """
        return RET_UNAVAILABLE

    def getLastError(self):
        """Retrieves the last error.

        :rtype: str
        """
        return self.lastError
