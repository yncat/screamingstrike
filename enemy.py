# -*- coding: utf-8 -*-
# Screaming Strike enemy handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)

"""This module contains enemy class."""
import bgtsound
import random
import globalVars
import window

STATE_ALIVE = 0
STATE_SCREAMING = 1
STATE_FALLING = 2
STATE_SHOULDBEDELETED = 3

SCREAM_PITCH_LOW=80
SCREAM_PITCH_HIGH=120
class Enemy():
	"""This class represents an enemy."""
	def __init__(self):
		self.scream=None
		self.bodyfall=None

	def __del__(self):
		self.field=None
		if self.scream is not None: self.scream.stop()
		if self.bodyfall is not None: self.bodyfall.stop()

	def initialize(self,field,x,speed,screamNum):
		"""Initializes this enemy.

		:param field: The field to which this enemy is bound.
		:type field: gameField.Field
		:param x: X position where this enemy spawns. The Y position is currently hardcoded to 20, so you can't change that.
		:type x: int
		:param speed: Speed of this enemy in milliseconds.
		:type speed: int
		:param screamNum: Scream file number.
		:type screamNum: int
		"""
		self.field=field
		self.x=x
		self.y=field.getY()
		self.speed=speed
		self.state=STATE_ALIVE
		self.stepTimer=window.Timer()
		self.screamNum=screamNum
		self.lastStepNum=-1

	def frameUpdate(self):
		"""Call this method once per frame to keep this enemy updated."""
		if self.state==STATE_SCREAMING and self.scream.playing is False: self.switchState(STATE_FALLING)
		if self.state==STATE_FALLING and self.bodyfall.playing is False: self.switchState(STATE_SHOULDBEDELETED)
		if self.state==STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		"""Changes this enemy's state. Internally called.

		:param newState: New state. STATE_**.
		:type newState: int
		"""
		self.state=newState
		if newState==STATE_FALLING: self.playBodyfall()

	def step(self):
		"""Makes this enemy walk one step. If it reaches to the player, it automatically attacks."""
		if self.attackCheck() is True: return
		self.y-=1
		s=bgtsound.sound()
		num=0
		while True:
			num=random.randint(1,18)
			if num!=self.lastStepNum: break
		# end while
		s.load(globalVars.appMain.sounds["s_lf%d.ogg" % num])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.pitch=random.randint(90,110)
		if self.y<4: s.pitch-=(4-self.y)*8
		s.play()
		self.stepTimer.restart()

	def attackCheck(self):
		"""Checks if this enemy can attack the player. If it can, it attacks."""
		if self.y!=0: return False
		self.field.player.hit()
		self.switchState(STATE_SHOULDBEDELETED)
		return True

	def hit(self):
		"""Kills this enemy as it got hit."""
		s=bgtsound.sound()
		s.load(globalVars.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		self.playScream()
		self.field.collectionCounter.inclement(self.screamNum)
		self.switchState(STATE_SCREAMING)
		score=(1000-self.speed)*(self.y+1)*(0.5+(0.5*self.field.level))*0.1
		if self.field.player.penetrate:
			score=score*2.0
			self.field.log(_("Hit! (speed %(speed)d, distance %(distance)d, penetration bonus added)") % {"speed": 900-self.speed, "distance": self.y})
		else:
			self.field.log(_("Hit! (speed %(speed)d, distance %(distance)d)") % {"speed": 900-self.speed, "distance": self.y})
		#end penetrate bonus
		self.field.player.addScore(score)

	def playScream(self):
		"""Makes this enemy scream. Internally called."""
		self.scream=bgtsound.sound()
		self.scream.load(globalVars.appMain.sounds["scream%d.ogg" % self.screamNum])
		self.scream.pitch=random.randint(SCREAM_PITCH_LOW,SCREAM_PITCH_HIGH)
		self.scream.pan=self.field.getPan(self.x)
		self.scream.volume=self.field.getVolume(self.y)
		self.scream.play()

	def playBodyfall(self):
		"""Makes a bodyfall sound for this enemy. Internally called."""
		self.bodyfall=bgtsound.sound()
		self.bodyfall.load(globalVars.appMain.sounds["dead.ogg"])
		self.bodyfall.pitch=random.randint(70,130)
		self.bodyfall.pan=self.field.getPan(self.x)
		self.bodyfall.volume=self.field.getVolume(self.y)
		self.bodyfall.play()
