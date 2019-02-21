# -*- coding: utf-8 -*-
#Screaming Strike main implementation
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
#import menu
import window
import sound_lib.sample
from bgtsound import *
#constants
MODE_NORMAL=0
MODE_ARCADE=1
MODEVAL_2_STR=["Normal","Arcade"]
GAME_RESULT_TERMINATE=0


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
		self.sounds["change.ogg"]=sound_lib.sample.Sample("sounds/change.ogg")
		self.sounds["fists.ogg"]=sound_lib.sample.Sample("sounds/fists.ogg")
		self.sounds["hit.ogg"]=sound_lib.sample.Sample("sounds/hit.ogg")
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
			if self.wnd.frameUpdate() is False: return False
			if self.wnd.keyPressing(window.K_ESCAPE): return False
			selected=m.frameUpdate()
			if selected==0 or selected==1: return selected
		#end loop
	#end mainmenu

	def run(self):
		if self.intro() is False: return
		selected=self.mainmenu()
		if selected is False: return
		result=self.gamePlay(selected)
		if result==GAME_RESULT_TERMINATE: return

	def gamePlay(self,mode):
		self.wnd.say("%s, start!" % MODEVAL_2_STR[mode])
		field=GameField()
		field.initialize(3,20,mode)
		player=Player()
		player.initialize(self,field)
		while(True):
			if self.wnd.frameUpdate() is False: return GAME_RESULT_TERMINATE
			if self.wnd.keyPressed(window.K_ESCAPE): return GAME_RESULT_TERMINATE
			player.frameUpdate()
#end class ssAppMain

class GameField():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,x,y,mode):
		self.x=x
		self.y=y
		self.mode=mode
		self.leftPanLimit=-100
		self.rightPanLimit=100

	def getCenterPosition(self):
		if self.x%2==0:
			return int((self.x/2)+1)
		else:
			return int(self.x/2)

	def getPan(self,pos):
		return self.leftPanLimit+(self.rightPanLimit-self.leftPanLimit)/(self.x-1)*pos

	def getX(self):
		return self.x

#end class GameField

class Player():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,appMain,field):
		self.appMain=appMain
		self.field=field
		self.lives=3
		self.x=field.getCenterPosition()
		self.punchTimer=window.Timer()

	def frameUpdate(self):
		if self.x!=0 and self.appMain.wnd.keyPressed(window.K_LEFT): self.moveTo(self.x-1)
		if self.x!=self.field.getX()-1 and self.appMain.wnd.keyPressed(window.K_RIGHT): self.moveTo(self.x+1)
	def moveTo(self,p):
		self.x=p
		s=sound()
		s.load(self.appMain.sounds["change.ogg"])
		s.pan=self.field.getPan(self.x)
		s.play()

