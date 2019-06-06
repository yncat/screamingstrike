# -*- coding: utf-8 -*-
# Screaming Strike game mode handlers
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import random
import item
import itemConstants
import window

NORMAL=0
ARCADE=1
CLASSIC=2
ALL_MODES_STR = ["Normal", "Arcade", "Classic"]

class ModeHandlerBase(object):
	def __init__(self):
		self.allowConsecutiveHitsBonus=True
		self.allowConsecutiveMissesBonus=False#Originally this was true, but I decided to disable it because the one of my friends (a professional game designer) said "In the game designing theory, subtracting scores is a totally bad idea!". And the penalty was very irritating, actually. lol!
		self.allowLevelupBonus=True
		self.name="Base"
		self.paused=False

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

	def getName(self):
		"""
		Retrieves the name of this mode. Normal, arcade or classic. There may be more future modes.

		:rtype: str
		"""
		return self.name

	def setPaused(self,p):
		"""Pauses / resumes this mode handler."""
		pass

class NormalModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()
		self.name=ALL_MODES_STR[0]

	def initialize(self,field):
		super().initialize(field)

class ArcadeModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()
		self.name=ALL_MODES_STR[1]

	def initialize(self,field):
		super().initialize(field)
		self.itemComingTimer=window.Timer()
		self.resetItemComingTimer()
		self.itemShowerTimer=window.Timer()
		self.resetItemShower()

	def frameUpdate(self):
		if self.itemShowerTimer.elapsed>=self.itemShowerTime: self.triggerItemShower()
		if self.itemComingTimer.elapsed>=self.itemComingTime: self.spawnItem()

	def setPaused(self,p):
		if p==self.paused: return
		self.paused=p
		self.itemComingTimer.setPaused(p)
		self.itemShowerTimer.setPaused(p)
	#end setPaused

	def triggerItemShower(self):
		self.spawnItem()
		self.itemShowerCount-=1
		if self.itemShowerCount==0:
			self.resetItemShower()
		else:
			self.itemShowerTime=150
			self.itemShowerTimer.restart()

	def resetItemShower(self):
		self.itemShowerTime=random.randint(70000,150000)
		self.itemShowerCount=random.randint(3,6)

	def spawnItem(self):
		spd=random.randint(100,800)
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
		self.name=ALL_MODES_STR[2]

	def calculateNextLevelup(self):
		"""
		This function provides classic mode specific formula.
		"""
		return int((2+self.field.level)*0.7)

def getModeHandler(mode):
	"""Receives a mode in string and returns the associated modeHandler object without initializing it.

	:param mode: Mode.
	:type mode: str
	"""
	if mode==ALL_MODES_STR[0]: return NormalModeHandler()
	if mode==ALL_MODES_STR[1]: return ArcadeModeHandler()
	if mode==ALL_MODES_STR[2]: return ClassicModeHandler()
	return None
