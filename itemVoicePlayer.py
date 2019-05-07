# -*- coding: utf-8 -*-
# Screaming Strike item voice player
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import glob
import os
import random
from bgtsound import *

class ItemVoicePlayer():
	def __init__(self):
		pass
	def __del__(self):
		pass

	def initialize(self,name):
		self.active=False
		if not os.path.exists("data/voices/%s" % name): return False
		self.sounds={}
		files=glob.glob("data/voices/%s/*.ogg" % name)
		if len(files)==0: return False
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
		self.name=name
		self.active=True

	def clear(self):
		self.sounds={}

	def test(self):
		if not self.active: return
		playOneShot(random.choice(list(self.sounds)))

	def play(self,file, pan):
		if not self.active: return
		if file in self.sounds:
			s=sound()
			s.load(self.sounds[file])
			s.pan=pan
			s.play()

