# -*- coding: utf-8 -*-
#Screaming Strike main implementation
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
#import menu
import window
from bgtsound import *
class ssAppMain():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self):
		"""Initializes the app. returns True on success or False on failure. """
		self.wnd=window.singletonWindow()
		ret=self.wnd.initialize(640,480,"Screaming Strike!")
		self.music=sound()
		self.music.load("sounds/bg.ogg")
		self.music.volume=-10
		return ret
	def intro(self):
		introsound=sound()
		introsound.load("sounds/ssIntro.ogg")
		introsound.play()
		while(introsound.playing):
			if self.wnd.frameUpdate() is False: sys.exit(0)
			if self.wnd.keyPressed(window.K_RETURN):
				introsound.fadeout(900)
				self.wnd.wait(1000)
				break
			#end skipping with enter
		#end while intro is playing
		self.music.play_looped()
	#end intro

	def mainmenu(self):
		while(True):
			if self.wnd.frameUpdate() is False: sys.exit(0)
			if self.wnd.keyPressing(window.K_ESCAPE): return
		#end loop
	#end mainmenu
#end class ssAppMain

