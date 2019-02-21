# -*- coding: utf-8 -*-
#Screaming Strike main implementation
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
import glob
import os
import math
import window
import sound_lib.sample
from bgtsound import *
#constants
MODE_NORMAL=0
MODE_ARCADE=1
MODEVAL_2_STR=["Normal","Arcade"]
GAME_RESULT_TERMINATE=0
ENEMY_STATE_ALIVE=0
ENEMY_STATE_SCREAMING=1
ENEMY_STATE_FALLING=2
ENEMY_STATE_SHOULDBEDELETED=3

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
		self.music.stream("sounds/stream/bg.ogg")
		self.music.volume=-10
		self.loadSounds()
		self.numScreams=len(glob.glob("sounds/scream*.ogg"))
		return ret

	def loadSounds(self):
		"""Preload ingame sounds into memory. This is for enhancing performance while playing the game. """
		self.sounds={}
		files=glob.glob("sounds/*.ogg")
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
	#end loadSounds

	def getNumScreams(self):
		return self.numScreams

	def intro(self):
		introsound=sound()
		introsound.stream("sounds/stream/ssIntro.ogg")
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
		field.initialize(self, 3,20,mode)
		while(True):
			if self.wnd.frameUpdate() is False: return GAME_RESULT_TERMINATE
			if self.wnd.keyPressed(window.K_ESCAPE): return GAME_RESULT_TERMINATE
			if field.frameUpdate() is False:break

#end class ssAppMain

class GameField():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,appMain, x,y,mode):
		self.appMain=appMain
		self.x=x
		self.y=y
		self.mode=mode
		self.leftPanLimit=-100
		self.rightPanLimit=100
		self.lowVolumeLimit=-30
		self.highVolumeLimit=0
		self.level=1
		self.enemies=[]
		self.enemies.append(None)
		self.player=Player()
		self.player.initialize(appMain,self)
		self.defeats=0
		self.nextLevelup=2

	def frameUpdate(self):
		self.player.frameUpdate()
		for i in range(self.level):
			if self.enemies[i] is not None and self.enemies[i].state==ENEMY_STATE_SHOULDBEDELETED: self.enemies[i]=None
			if self.enemies[i] is not None: self.enemies[i].frameUpdate()
			if self.enemies[i] is None: self.spawnEnemy(i)

	def spawnEnemy(self,slot):
		e=Enemy()
		e.initialize(self.appMain,self,self.player,random.randint(0,self.x-1),random.randint(300,900),random.randint(1,self.appMain.getNumScreams()))
		self.enemies[slot]=e

	def logDefeat(self):
		self.defeats+=1
		self.nextLevelup-=1
		if self.nextLevelup==0: self.levelup()

	def levelup(self):
		self.level+=1
		self.enemies.append(None)
		self.nextLevelup=1+self.level
		self.appMain.wnd.say("Level %d!" % self.level)

	def getCenterPosition(self):
		if self.x%2==0:
			return int((self.x/2)+1)
		else:
			return int(self.x/2)

	def getPan(self,pos):
		return self.leftPanLimit+(self.rightPanLimit-self.leftPanLimit)/(self.x-1)*pos

	def getVolume(self,pos):
		return self.highVolumeLimit-(self.highVolumeLimit-self.lowVolumeLimit)/self.y*pos

	def getX(self):
		return self.x

	def getY(self):
		return self.y


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
		self.punchTimer=window.Timer()
		self.punching=False
		self.punchHitTime=200
		self.punchRange=4

	def frameUpdate(self):
		if self.punching is False and self.appMain.wnd.keyPressed(window.K_SPACE): self.punchLaunch()
		if self.punching is True and self.punchTimer.elapsed>=self.punchHitTime: self.punchHit()
		if self.x!=0 and self.appMain.wnd.keyPressed(window.K_LEFT): self.moveTo(self.x-1)
		if self.x!=self.field.getX()-1 and self.appMain.wnd.keyPressed(window.K_RIGHT): self.moveTo(self.x+1)

	def punchLaunch(self):
		self.punching=True
		s=sound()
		s.load(self.appMain.sounds["fists.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(90,110)
		s.play()
		self.punchTimer.restart()

	def punchHit(self):
		self.punching=False
		for elem in self.field.enemies:
			if elem.state==ENEMY_STATE_ALIVE and self.x==elem.x and elem.y<=self.punchRange:
				elem.hit()
				self.field.logDefeat()
				break

	def moveTo(self,p):
		self.x=p
		s=sound()
		s.load(self.appMain.sounds["change.ogg"])
		s.pan=self.field.getPan(self.x)
		s.play()

	def hit(self):
		self.lives-=1
		s=sound()
		if self.lives>0:
			s.load(self.appMain.sounds["attacked.ogg"])
			s.play()
		else:
			s.load(self.appMain.sounds["gameover.ogg"])
			s.volume=-10
			s.play()


#end class Player

class Enemy():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,appMain,field,player,x,speed,screamNum):
		self.appMain=appMain
		self.field=field
		self.player=player
		self.x=x
		self.y=field.getY()
		self.speed=speed
		self.state=ENEMY_STATE_ALIVE
		self.stepTimer=window.Timer()
		self.screamNum=screamNum
		self.lastStepNum=-1

	def frameUpdate(self):
		if self.state==ENEMY_STATE_SCREAMING and self.scream.playing is False: self.switchState(ENEMY_STATE_FALLING)
		if self.state==ENEMY_STATE_FALLING and self.bodyfall.playing is False: self.switchState(ENEMY_STATE_SHOULDBEDELETED)
		if self.state==ENEMY_STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		self.state=newState
		if newState==ENEMY_STATE_FALLING: self.playBodyfall()

	def step(self):
		if self.hitCheck() is True: return
		self.y-=1
		s=sound()
		num=0
		while True:
			num=random.randint(1,18)
			if num!=self.lastStepNum: break
		#end while
		s.load(self.appMain.sounds["s_lf%d.ogg" % num])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.pitch=random.randint(90,110)
		s.play()
		self.stepTimer.restart()

	def hitCheck(self):
		if self.y!=0: return False
		self.player.hit()
		self.switchState(ENEMY_STATE_SHOULDBEDELETED)
		return True

	def hit(self):
		s=sound()
		s.load(self.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.pitch=random.randint(70,130)
		s.play()
		self.playScream()
		self.switchState(ENEMY_STATE_SCREAMING)

	def playScream(self):
		self.scream=sound()
		self.scream.load(self.appMain.sounds["scream%d.ogg" % self.screamNum])
		self.scream.pitch=random.randint(80,120)
		self.scream.pan=self.field.getPan(self.x)
		self.scream.volume=self.field.getVolume(self.y)
		self.scream.play()

	def playBodyfall(self):
		self.bodyfall=sound()
		self.bodyfall.load(self.appMain.sounds["dead.ogg"])
		self.bodyfall.pitch=random.randint(70,130)
		self.bodyfall.pan=self.field.getPan(self.x)
		self.bodyfall.volume=self.field.getVolume(self.y)
		self.bodyfall.play()
