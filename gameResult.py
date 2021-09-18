# -*- coding: utf-8 -*-
# Screaming Strike game results class
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
"""This module contains GameResult class."""


class GameResult:
    """This class stores a gameplay's result. """

    def __init__(self):
        self.aborted = False

    def __del__(self):
        pass

    def initialize(self, field):
        """
        Populates the game results from the given field instance.

        :param field: Field instance from which the game results are loaded.
        :type field: gameField.GameField
        """
        self.score = field.player.score
        self.score_validator = field.player.score_validator
        self.hitPercentage = field.player.hitPercentage
        self.hits = field.player.hits
        self.punches = field.player.punches
        self.level = field.level
        self.mode = field.modeHandler.getName()
        self.unlockedCollection = field.collectionCounter.getLog()
        self.highscore = field.player.getNewHighscore()
        self.previousHighscore = field.player.getPreviousHighscore()
        self.log = field.getLog()
        ms = field.gameTimer.elapsed
        self.lastedMinute = int(ms / 60000)
        self.lastedSecond = int((ms % 60000) / 1000)
        m = _("minute") if self.lastedMinute == 1 else _("minutes")
        s = _("second") if self.lastedSecond == 1 else _("seconds")
        self.lastedString = _("%(min)d %(minunit)s and %(sec)d %(secunit)s") % {
            "min": self.lastedMinute, "minunit": m, "sec": self.lastedSecond, "secunit": s}
    # end initialize

    def getaborted(self):
        """Retrieves if this game was ended by abort (ESC)."""
        return self.aborted
    # end aborted

    def setaborted(self, abt):
        """Set the abort status of this result.

        :param abt: aborted?
        :type abt: bool
        """
        self.aborted = abt

    def validateScore(self):
        """Returns if the score is valid (not modified by memory hacking).

        :rtype: bool
        """
        return self.score == sum(self.score_validator)
