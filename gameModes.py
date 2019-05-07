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

class NormalModeHandler(object):
	def __init__(self):
		pass
	def __del__(self):
		self.field=None
	def initialize(self,field):
		self.field=field
	def frameUpdate(self):
		pass

class ArcadeModeHandler(NormalModeHandler):
	def __init__(self):
		super().__init__()
	def __del__(self):
		super().__del__()
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
