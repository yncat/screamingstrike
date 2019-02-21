# -*- coding: utf-8 -*-
#Screaming Strike main implementation
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
#import menu
import window
import sound_lib.sample
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
		self.music.stream("sounds/bg.ogg")
		self.music.volume=-10
		self.loadSounds()
		return ret

	def loadSounds(self):
		"""Preload ingame sounds into memory. This is for enhancing performance while playing the game. """
		self.sounds={}
		#Footsteps on leaves
		for i in range(1,18):
			name="s_lf%d.ogg" % i
			self.sounds[name]=sound_lib.sample.Sample("sounds/"+name)
		#end steps on leaves
	#end loadSounds

	def intro(self):
		introsound=sound()
		introsound.stream("sounds/ssIntro.ogg")
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
		m=window.menu()
		m.initialize(self.wnd,"Please choose an option","Normal mode#Arcade mode#Exit")
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: sys.exit(0)
			if self.wnd.keyPressing(window.K_ESCAPE): return
			selected=m.frameUpdate()
			if selected==0 or selected==1: sys.exit(0)
		#end loop
	#end mainmenu
#end class ssAppMain

