# -*- coding: utf-8 -*-
# Screaming Strike item voice player
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import glob
import os
import random
import bgtsound


class ItemVoicePlayer():
    def __init__(self):
        pass

    def __del__(self):
        pass

    def initialize(self, name):
        self.active = False
        if not os.path.exists("data/voices/%s" % name):
            return False
        self.sounds = {}
        files = glob.glob("data/voices/%s/*.ogg" % name)
        if len(files) == 0:
            return False
        for elem in files:
            self.sounds[os.path.basename(elem)] = bgtsound.sound_lib.sample.Sample(elem)
        self.name = name
        self.active = True
        return True

    def clear(self):
        self.sounds = {}

    def test(self):
        if not self.active:
            return
        self.testSound = bgtsound.sound()
        self.testSound.load(random.choice(list(self.sounds.values())))
        self.testSound.volume = -10
        self.testSound.play()

    def play(self, file, pan):
        if not self.active:
            return
        if file in self.sounds:
            s = bgtsound.sound()
            s.load(self.sounds[file])
            s.pan = pan
            s.play()
