# -*- coding: utf-8 -*-
# Screaming Strike item handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import random

import bgtsound
import globalVars
from itemConstants import *
import window

class Item():
	def __init__(self):
		self.fallingBeep=None
		self.shatter=None

	def __del__(self):
		self.field=None
		if self.fallingBeep is not None: self.fallingBeep.stop()
		if self.shatter is not None: self.shatter.stop()

	def initialize(self,field,x,speed,type,identifier):
		self.field=field
		self.x=x
		self.y=field.getY()
		self.speed=speed
		self.state=STATE_ALIVE
		self.stepTimer=window.Timer()
		self.fallingBeep=bgtsound.sound()
		self.fallingBeep.load(globalVars.appMain.sounds["itemfalling.ogg"])
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.fallingBeep.play_looped()
		self.type=type
		self.identifier=identifier

	def frameUpdate(self):
		if self.state==STATE_BROKEN and self.shatter.playing is False: self.switchState(STATE_SHOULDBEDELETED)
		if self.state==STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		self.state=newState
		if newState==STATE_BROKEN: self.playShatter()

	def step(self):
		if self.destroyCheck() is True: return
		self.y-=1
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.stepTimer.restart()

	def destroyCheck(self):
		if self.y!=0: return False
		self.switchState(STATE_BROKEN)
		self.field.log(_("A \"%(item)s\" item fell on the ground and shattered into peaces!") % {"item": NAMES[self.type][self.identifier]})
		return True

	def obtain(self):
		self.field.log(_("Obtained a \"%(item)s\" item!") % {"item": NAMES[self.type][self.identifier]})
		s=bgtsound.sound()
		s.load(globalVars.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		s=bgtsound.sound()
		s.load(globalVars.appMain.sounds["itemget.ogg"])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.play()
		self.field.itemVoicePlayer.play("get %s.ogg" % NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.fallingBeep.stop()
		self.switchState(STATE_SHOULDBEDELETED)

	def punch(self):
		"""Called when this item was punched and destroyed."""
		s=bgtsound.sound()
		s.load(globalVars.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		self.destroy()


	def destroy(self):
		self.field.log(_("A \"%(item)s\" item was shattered into peaces!") % {"item": NAMES[self.type][self.identifier]})
		self.switchState(STATE_BROKEN)

	def playShatter(self):
		self.field.itemVoicePlayer.play("lose %s.ogg" % NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.shatter=bgtsound.sound()
		self.shatter.load(globalVars.appMain.sounds["item_destroy%d.ogg" % random.randint(1,2)])
		self.shatter.pitch=random.randint(70,130)
		self.shatter.pan=self.field.getPan(self.x)
		self.shatter.volume=self.field.getVolume(self.y)
		self.shatter.play()
		self.fallingBeep.stop()

