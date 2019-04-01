# -*- coding: utf-8 -*-
# Screaming Strike enemy handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

from bgtsound import *
import random
import globalVars
import window

STATE_ALIVE = 0
STATE_SCREAMING = 1
STATE_FALLING = 2
STATE_SHOULDBEDELETED = 3

class Enemy():
	def __init__(self):
		self.scream=None
		self.bodyfall=None

	def __del__(self):
		self.field=None
		if self.scream is not None: self.scream.stop()
		if self.bodyfall is not None: self.bodyfall.stop()

	def initialize(self,field,x,speed,screamNum):
		self.field=field
		self.x=x
		self.y=field.getY()
		self.speed=speed
		self.state=STATE_ALIVE
		self.stepTimer=window.Timer()
		self.screamNum=screamNum
		self.lastStepNum=-1

	def frameUpdate(self):
		if self.state==STATE_SCREAMING and self.scream.playing is False: self.switchState(STATE_FALLING)
		if self.state==STATE_FALLING and self.bodyfall.playing is False: self.switchState(STATE_SHOULDBEDELETED)
		if self.state==STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		self.state=newState
		if newState==STATE_FALLING: self.playBodyfall()

	def step(self):
		if self.attackCheck() is True: return
		self.y-=1
		s=sound()
		num=0
		while True:
			num=random.randint(1,18)
			if num!=self.lastStepNum: break
		# end while
		s.load(globalVars.appMain.sounds["s_lf%d.ogg" % num])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.pitch=random.randint(90,110)
		s.play()
		self.stepTimer.restart()

	def attackCheck(self):
		if self.y!=0: return False
		self.field.player.hit()
		self.switchState(STATE_SHOULDBEDELETED)
		return True

	def hit(self):
		s=sound()
		s.load(globalVars.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		self.playScream()
		self.switchState(STATE_SCREAMING)
		score=(1000-self.speed)*(self.y+1)*(0.5+(0.5*self.field.level))*0.1
		self.field.log(_("Hit! (speed %(speed)d, distance %(distance)d)") % {"speed": 900-self.speed, "distance": self.y})
		self.field.player.addScore(score)

	def playScream(self):
		self.scream=sound()
		self.scream.load(globalVars.appMain.sounds["scream%d.ogg" % self.screamNum])
		self.scream.pitch=random.randint(80,120)
		self.scream.pan=self.field.getPan(self.x)
		self.scream.volume=self.field.getVolume(self.y)
		self.scream.play()

	def playBodyfall(self):
		self.bodyfall=sound()
		self.bodyfall.load(globalVars.appMain.sounds["dead.ogg"])
		self.bodyfall.pitch=random.randint(70,130)
		self.bodyfall.pan=self.field.getPan(self.x)
		self.bodyfall.volume=self.field.getVolume(self.y)
		self.bodyfall.play()
