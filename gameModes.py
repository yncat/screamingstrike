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
BURDEN=3
ALL_MODES_STR = ["Normal", "Arcade", "Classic", "Burden"]

class ModeHandlerBase(object):
	def __init__(self):
		self.allowConsecutiveHitsBonus=True
		self.allowConsecutiveMissesBonus=False#Originally this was true, but I decided to disable it because the one of my friends (a professional game designer) said "In the game designing theory, subtracting scores is a totally bad idea!". And the penalty was very irritating, actually. lol!
		self.allowLevelupBonus=True
		self.name="Base"
		self.paused=False

	def initialize(self,field):
		self.field=field

	def frameUpdate(self):
		pass

	def calculateNextLevelup(self):
		"""
		Calculates the number of enemies that should be defeated in this mode. This function implements the default formula. 
		"""
		if self.field.level==1: return 2
		r=int(1+(self.field.level*self.field.level*0.25))
		if r>60: r=60
		return r

	def getShrinkMultiplier(self):
		"""
			Defines the multiplier amount of the shrink item effect in this mode, Default is 0.5 (half length).

			:rtype multiplier: float
		"""
		return 0.5

	def getSlowDownMultiplier(self):
		"""
			Defines the multiplier amount of the slow down item effect in this mode, Default is 2.0 (2x motion time).

			:rtype multiplier: float
		"""
		return 2.0

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
		ident = self.selectNastyItem() if t==item.TYPE_NASTY else random.randint(0,item.GOOD_MAX)
		i=item.Item()
		i.initialize(self.field,random.randint(0,self.field.x-1),spd,t,ident)
		self.field.items.append(i)
		self.resetItemComingTimer()

	def selectNastyItem(self):
		"""Prevents shrink from appearing when the player already has 2 shrink effects."""
		shrinks = len([e for e in self.field.player.itemEffects if e.name == itemConstants.NAMES[itemConstants.TYPE_NASTY][itemConstants.NASTY_SHRINK]])
		while(True):
			ret = random.randint(0,itemConstants.NASTY_MAX)
			if ret == itemConstants.NASTY_SHRINK and shrinks==2: continue
			break
		return ret

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

class BurdenModeHandler(ModeHandlerBase):
	def __init__(self):
		super().__init__()
		self.name=ALL_MODES_STR[3]

	def initialize(self,field):
		super().initialize(field)
		self.itemComingTimer=window.Timer()
		self.resetItemComingTimer()
		self.itemShowerTimer=window.Timer()
		self.resetItemShower()

	def getShrinkMultiplier(self):
		return 0.75

	def getSlowDownMultiplier(self):
		return 1.5

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
		t=itemConstants.TYPE_NASTY
		ident=self.selectNastyItem()
		i=item.Item()
		i.initialize(self.field,random.randint(0,self.field.x-1),spd,t,ident)
		self.field.items.append(i)
		self.resetItemComingTimer()

	def selectNastyItem(self):
		"""Prevents shrink from appearing when the player already has 3 shrink effects."""
		shrinks = len([e for e in self.field.player.itemEffects if e.name == itemConstants.NAMES[itemConstants.TYPE_NASTY][itemConstants.NASTY_SHRINK]])
		while(True):
			ret = random.randint(0,itemConstants.NASTY_MAX)
			if ret == itemConstants.NASTY_SHRINK and shrinks==3: continue
			break
		return ret

	def resetItemComingTimer(self):
		self.itemComingTimer.restart()
		self.itemComingTime=random.randint(0,60000)


def getModeHandler(mode):
	"""Receives a mode in string and returns the associated modeHandler object without initializing it.

	:param mode: Mode.
	:type mode: str
	"""
	if mode==ALL_MODES_STR[0]: return NormalModeHandler()
	if mode==ALL_MODES_STR[1]: return ArcadeModeHandler()
	if mode==ALL_MODES_STR[2]: return ClassicModeHandler()
	if mode==ALL_MODES_STR[3]: return BurdenModeHandler()
	return None
