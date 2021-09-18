# -*- coding: utf-8 -*-
# Screaming Strike game options handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import locale
import os
import pickle


class GameOptions:
    def __init__(self):
        self.BGMVOLUME_NEGATIVE_BOUNDARY = -30
        self.BGMVOLUME_POSITIVE_BOUNDARY = 0
        self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY = -100
        self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY = -20
        self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY = 20
        self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY = 100

    def __del__(self):
        pass

    def initialize(self, importer):
        if isinstance(importer, GameOptions):
            self.copyFrom(importer)
        elif isinstance(importer, str):
            self.load(importer)
        else:
            self.setDefault()

    def setDefault(self):
        self.bgmVolume = -10
        self.leftPanningLimit = -100
        self.rightPanningLimit = 100
        self.itemVoice = "chris"
        self.language = locale.getdefaultlocale()[0]
        if self.language is None:
            self.language = "en_US"  # OSX may fail to auto language detect when frozen
        if not os.path.isdir("locale/%s" % self.language):
            self.language = "en_US"  # No such locale in the game

    def copyFrom(self, importer):
        self.bgmVolume = importer.bgmVolume
        self.leftPanningLimit = importer.leftPanningLimit
        self.rightPanningLimit = importer.rightPanningLimit
        self.itemVoice = importer.itemVoice
        self.language = importer.language

    def load(self, filename):
        if os.path.isfile(filename) is not True:
            self.setDefault()
            self.save(filename)
            return False
        with open(filename, mode='r') as f:
            values = f.read().split("#")
        # end with
        numValues = len(values)
        self.bgmVolume = int(values[0])
        if self.bgmVolume < self.BGMVOLUME_NEGATIVE_BOUNDARY:
            self.bgmVolume = self.BGMVOLUME_NEGATIVE_BOUNDARY
        if self.bgmVolume > self.BGMVOLUME_POSITIVE_BOUNDARY:
            self.bgmVolume = self.BGMVOLUME_POSITIVE_BOUNDARY
        self.leftPanningLimit = int(values[1])
        if self.leftPanningLimit < self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY:
            self.leftPanningLimit = self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY
        if self.leftPanningLimit > self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY:
            self.leftPanningLimit = self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY
        self.rightPanningLimit = int(values[2])
        if self.rightPanningLimit > self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY:
            self.rightPanningLimit = self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY
        if self.rightPanningLimit < self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY:
            self.rightPanningLimit = self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY
        self.itemVoice = values[3]
        self.language = values[4] if numValues > 4 else locale.getdefaultlocale()[0]
        return True

    def save(self, filename):
        s = "%d#%d#%d#%s#%s" % (self.bgmVolume, self.leftPanningLimit, self.rightPanningLimit, self.itemVoice, self.language)
        with open(filename, mode="w") as f:
            f.write(s)
