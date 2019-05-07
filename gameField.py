# -*- coding: utf-8 -*-
# Screaming Strike game field
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import datetime
import random
from bgtsound import *
import bonusCounter
import enemy
import gameModes
import globalVars
import item
import itemConstants
import itemVoicePlayer
import player
import window

class GameField():
	def __init__(self):
		pass
	def __del__(self):
		self.Enemies=None
		self.player=None

	def initialize(self, x,y,mode, voice):
		self.x=x
		self.y=y
		self.setModeHandler(mode)
		self.leftPanningLimit=-100
		self.rightPanningLimit=100
		self.lowVolumeLimit=-30
		self.highVolumeLimit=0
		self.level=1
		self.enemies=[]
		self.items=[]
		self.enemies.append(None)
		self.player=player.Player()
		self.player.initialize(self)
		self.defeats=0
		self.nextLevelup=2
		self.levelupBonus=bonusCounter.BonusCounter()
		self.levelupBonus.initialize()
		self.destructing=False
		self.destructTimer=window.Timer()
		self.itemVoicePlayer=itemVoicePlayer.ItemVoicePlayer()
		self.itemVoicePlayer.initialize(voice)
		self.logs=[]
		self.log(_("Game started at %(startedtime)s!") % {"startedtime": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")})

	def setModeHandler(self,mode):
		if mode==gameModes.NORMAL:
			self.modeHandler=NormalModeHandler()
		elif mode==gameModes.ARCADE:
			self.modeHandler=gameModes.ArcadeModeHandler()
		elif mode==gameModes.CLASSIC:
			self.modeHandler=gameModes.ClassicModeHandler()
		# end if
		self.modeHandler.initialize(self)

	def setLimits(self,lpLimit, rpLimit):
		self.leftPanningLimit=lpLimit
		self.rightPanningLimit=rpLimit

	def frameUpdate(self):
		if self.destructing:
			if self.destructTimer.elapsed>=1800: self.performDestruction()
			return True
		# end if destruct
		self.player.frameUpdate()
		if self.player.lives<=0:
			self.log(_("Game over! Final score: %(score)d") % {"score": self.player.score})
			return False
		# end if
		self.modeHandler.frameUpdate()
		self.levelupBonus.frameUpdate()
		for i in range(self.level):
			if self.enemies[i] is not None and self.enemies[i].state==enemy.STATE_SHOULDBEDELETED: self.enemies[i]=None
			if self.enemies[i] is not None: self.enemies[i].frameUpdate()
			if self.enemies[i] is None: self.spawnEnemy(i)
		# end for
		for elem in self.items[:]:
			if elem is not None and elem.state==itemConstants.STATE_SHOULDBEDELETED: self.items.remove(elem)
			if elem is not None: elem.frameUpdate()
		return True

	def spawnEnemy(self,slot):
		e=enemy.Enemy()
		e.initialize(self,random.randint(0,self.x-1),random.randint(300,900),random.randint(1,globalVars.appMain.getNumScreams()))
		self.enemies[slot]=e

	def logDefeat(self):
		self.defeats+=1
		self.nextLevelup-=1
		if self.nextLevelup==0: self.levelup()

	def log(self,s):
		self.logs.append(s)

	def exportLog(self):
		return "\n".join(self.logs)

	def levelup(self):
		if self.player.lives>1:
			self.log(_("Leveled up to %(newlevel)d! (Accuracy %(accuracy).1f%%, with %(lives)d lives remaining)") % {"newlevel": self.level, "accuracy": self.player.hitPercentage, "lives": self.player.lives})
		else:
			self.log(_("Leveled up to %(newlevel)d! (Accuracy %(accuracy).1f%%, with %(lives)d life remaining)") % {"newlevel": self.level, "accuracy": self.player.hitPercentage, "lives": self.player.lives})
	# end if 
		self.processLevelupBonus()
		self.level+=1
		self.enemies.append(None)
		self.nextLevelup=int(1+(self.level*self.level*0.25))
		globalVars.appMain.changeMusicPitch_relative(5)

	def processLevelupBonus(self):
		if not self.modeHandler.allowLevelupBonus: return
		self.player.addScore(self.player.hitPercentage*self.player.hitPercentage*self.level*self.player.lives*0.5)
		self.levelupBonus.start(int(self.player.hitPercentage*0.1))

	def getCenterPosition(self):
		if self.x%2==0:
			return int((self.x/2)+1)
		else:
			return int(self.x/2)

	def getPan(self,pos):
		return self.leftPanningLimit+(self.rightPanningLimit-self.leftPanningLimit)/(self.x-1)*pos

	def getVolume(self,pos):
		return self.highVolumeLimit-(self.highVolumeLimit-self.lowVolumeLimit)/self.y*pos

	def getPitch(self,y):
		return 70+(y*3)

	def getX(self):
		return self.x

	def getY(self):
		return self.y

	def clear(self):
		self.enemies=[]
		self.items=[]

	def startDestruction(self):
		if self.destructing: return
		playOneShot(globalVars.appMain.sounds["destructPowerup.ogg"])
		self.destructTimer.restart()
		self.destructing=True

	def performDestruction(self):
		playOneShot(globalVars.appMain.sounds["destruct.ogg"])
		self.log(_("Activating destruction!"))
		for elem in self.enemies:
			if elem is not None and elem.state==enemy.STATE_ALIVE: elem.hit()
			self.logDefeat()
		for elem in self.items:
			elem.destroy()
		self.destructing=False
		self.log(_("End destruction!"))
# end class GameField
