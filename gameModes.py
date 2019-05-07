# -*- coding: utf-8 -*-
# Screaming Strike game mode handlers
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import random
from bgtsound import *
import item
import itemConstants
import window

NORMAL=0
ARCADE=1
CLASSIC=2
NAME_STR = ["Normal", "Arcade", "Classic"]

class ModeHandlerBase(object):
	def __init__(self):
		self.allowConsecutiveHitsBonus=True
		self.allowConsecutiveMissesBonus=True
		self.allowLevelupBonus=True

	def __del__(self):
		self.field=None

	def initialize(self,field):
		self.field=field

	def frameUpdate(self):
		pass

	def calculateNextLevelup(self):
		"""
Calculates the number of enemies that should be defeated in this mode. This function implements the default formula. 
"""
		if self.field.level==1: return 2
		return int(1+(self.field.level*self.field.level*0.25))

class NormalModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()

	def initialize(self,field):
		super().initialize(field)

class ArcadeModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()

	def initialize(self,field):
		super().initialize(field)
		self.itemComingTimer=window.Timer()
		self.resetItemComingTimer()
		self.itemShowerTimer=window.Timer()
		self.resetItemShower()

	def frameUpdate(self):
		if self.itemShowerTimer.elapsed>=self.itemShowerTime: self.triggerItemShower()
		if self.itemComingTimer.elapsed>=self.itemComingTime: self.spawnItem()

	def triggerItemShower(self):
		self.spawnItem()
		self.itemShowerCount-=1
		if self.itemShowerCount==0:
			self.resetItemShower()
		else:
			self.itemShowerTime=150
			self.itemShowerTimer.restart()

	def resetItemShower(self):
		self.itemShowerTime=90000
		self.itemShowerCount=random.randint(3,6)

	def spawnItem(self):
		spd=random.randint(100,900)
		t=itemConstants.TYPE_NASTY if random.randint(1,100)<=spd/10 else itemConstants.TYPE_GOOD
		ident=random.randint(0,itemConstants.NASTY_MAX) if t==item.TYPE_NASTY else random.randint(0,item.GOOD_MAX)
		i=item.Item()
		i.initialize(self.field,random.randint(0,self.field.x-1),spd,t,ident)
		self.field.items.append(i)
		self.resetItemComingTimer()

	def resetItemComingTimer(self):
		self.itemComingTimer.restart()
		self.itemComingTime=random.randint(0,60000)

class ClassicModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()
		#disable bonuses
		self.allowConsecutiveHitsBonus=False
		self.allowConsecutiveMissesBonus=False
		self.allowLevelupBonus=False

	def calculateNextLevelup(self):
		"""
This function provides classic mode specific formula.
"""
		return int((2+self.field.level)*0.7)
