# -*- coding: utf-8 -*-
#Screaming Strike main implementation
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
import glob
import os
import threading
import datetime
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
		self.thread_loadSounds=threading.Thread(target=self.loadSounds)
		self.thread_loadSounds.setDaemon(True)
		self.thread_loadSounds.start()
		self.options=GameOptions()
		self.options.initialize("data/options.dat")
		self.wnd=window.singletonWindow()
		ret=self.wnd.initialize(640,480,"Screaming Strike!")
		self.music=sound()
		self.music.stream("data/sounds/stream/bg.ogg")
		self.music.volume=self.options.bgmVolume
		self.numScreams=len(glob.glob("data/sounds/scream*.ogg"))
		return ret

	def loadSounds(self):
		"""Preload ingame sounds into memory. This is for enhancing performance while playing the game. """
		self.sounds={}
		files=glob.glob("data/sounds/*.ogg")
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
	#end loadSounds

	def getNumScreams(self):
		return self.numScreams

	def intro(self):
		introsound=sound()
		introsound.stream("data/sounds/stream/ssIntro.ogg")
		introsound.play()
		while(introsound.playing):
			if self.wnd.frameUpdate() is False: sys.exit(0)
			if self.wnd.keyPressed(window.K_RETURN):
				introsound.fadeout(900)
				self.wnd.wait(1000)
				break
			#end skipping with enter
		#end while intro is playing
		self.thread_loadSounds.join()
		self.music.play_looped()
	#end intro

	def mainmenu(self):
		m=window.menu()
		m.initialize(self.wnd,"Main menu. Use your up and down arrows to choose an option, then press enter to confirm","Normal mode#Arcade mode#Options#Exit",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			if self.wnd.keyPressed(window.K_ESCAPE): return False
			selected=m.frameUpdate()
			if selected is not None and selected>=0: return selected
		#end loop
	#end mainmenu

	def run(self):
		if self.intro() is False: return
		while(True):
			selected=self.mainmenu()
			if selected is False or selected==3: return
			if selected==2:
				if self.optionsMenu() is False: return
				continue
			#end if
			result=self.gamePlay(selected)
			if result==GAME_RESULT_TERMINATE: return
			if self.resultScreen(result) is False: return

	def optionsMenu(self):
		backup=GameOptions()
		backup.initialize(self.options)
		m=window.menu()
		m.initialize(self.wnd,"Options Menu, use your up and down arrows to choose an option, left and right arrows to change values, enter to save or escape to discard changes","",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.add("Background music volume")
		m.add("Left panning limit")
		m.add("Right panning limit.")
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			ret=m.frameUpdate()
			if self.wnd.keyPressed(window.K_LEFT): self.optionChange(m.getCursorPos(),-1)
			if self.wnd.keyPressed(window.K_RIGHT): self.optionChange(m.getCursorPos(),1)
			if ret is None: continue
			if ret==-1: 
				self.options=GameOptions()
				self.options.initialize(backup)
				self.wnd.say("Changes discarded.")
				self.music.volume=self.options.bgmVolume
				return True
			#end if
			if ret>=0:
				self.wnd.say("Settings saved")
				self.options.save("data/options.dat")
				return True

	def optionChange(self,cursor,direction):
		if cursor==0:#BGM volume
			if direction==1 and self.options.bgmVolume==self.options.BGMVOLUME_POSITIVE_BOUNDARY: return
			if direction==-1 and self.options.bgmVolume==self.options.BGMVOLUME_NEGATIVE_BOUNDARY: return
			if direction==1: self.options.bgmVolume+=2
			if direction==-1: self.options.bgmVolume-=2
			self.music.volume=self.options.bgmVolume
			self.wnd.say("%d" % (abs(-30-self.options.bgmVolume)*0.5))
			return
		#end bgm volume
		if cursor==1:#left panning limit
			if direction==1 and self.options.leftPanningLimit==self.options.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY: return
			if direction==-1 and self.options.leftPanningLimit==self.options.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY: return
			if direction==1: self.options.leftPanningLimit+=5
			if direction==-1: self.options.leftPanningLimit-=5
			s=sound()
			s.load(self.sounds["change.ogg"])
			s.pan=self.options.leftPanningLimit
			s.play()
			return
	#end left panning limit
		if cursor==2:#right panning limit
			if direction==1 and self.options.rightPanningLimit==self.options.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY: return
			if direction==-1 and self.options.rightPanningLimit==self.options.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY: return
			if direction==1: self.options.rightPanningLimit+=5
			if direction==-1: self.options.rightPanningLimit-=5
			s=sound()
			s.load(self.sounds["change.ogg"])
			s.pan=self.options.rightPanningLimit
			s.play()
		return
		#end left panning limit
	#end optionChange

	def gamePlay(self,mode):
		self.wnd.say("%s, start!" % MODEVAL_2_STR[mode])
		field=GameField()
		field.initialize(self, 3,20,mode)
		field.setLimits(self.options.leftPanningLimit,self.options.rightPanningLimit)
		while(True):
			if self.wnd.frameUpdate() is False: return GAME_RESULT_TERMINATE
			if self.wnd.keyPressed(window.K_ESCAPE): return GAME_RESULT_TERMINATE
			if field.frameUpdate() is False:break
		#end while
		field.clear()
		if self.wnd.wait(2000)==False: return GAME_RESULT_TERMINATE
		s=sound()
		s.load(self.sounds["dead.ogg"])
		s.pitch=random.randint(70,130)
		s.play()
		if self.wnd.wait(800)==False: return GAME_RESULT_TERMINATE
		with open("result.txt", mode='a') as f:
			f.write(field.exportLog())
		r=GameResult()
		r.initialize(field)
		return r

	def resultScreen(self,result):
		m=window.menu()
		m.initialize(self.wnd,"Game result","",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.add("Final score: %d" % result.score)
		m.add("Punches: %d, hits: %d, accuracy: %.2f%%" % (result.punches, result.hits, result.hitPercentage))
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			r=m.frameUpdate()
			if r is not None:break
		#end while
		return True



#end class ssAppMain

class GameField():
	def __init__(self):
		pass
	def __del__(self):
		self.Enemies=None
		self.player=None

	def initialize(self,appMain, x,y,mode):
		self.appMain=appMain
		self.x=x
		self.y=y
		self.mode=mode
		self.leftPanningLimit=-100
		self.rightPanningLimit=100
		self.lowVolumeLimit=-30
		self.highVolumeLimit=0
		self.level=1
		self.enemies=[]
		self.enemies.append(None)
		self.player=Player()
		self.player.initialize(appMain,self)
		self.defeats=0
		self.nextLevelup=2
		self.levelupBonus=BonusCounter()
		self.levelupBonus.initialize(self.appMain)
		self.logs=[]
		self.log("Game started at %s!" % datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

	def setLimits(self,lpLimit, rpLimit):
		self.leftPanningLimit=lpLimit
		self.rightPanningLimit=rpLimit

	def frameUpdate(self):
		self.player.frameUpdate()
		if self.player.lives<=0:
			self.log("Game over! Final score: %d" % self.player.score)
			return False
		#end if
		self.levelupBonus.frameUpdate()
		for i in range(self.level):
			if self.enemies[i] is not None and self.enemies[i].state==ENEMY_STATE_SHOULDBEDELETED: self.enemies[i]=None
			if self.enemies[i] is not None: self.enemies[i].frameUpdate()
			if self.enemies[i] is None: self.spawnEnemy(i)
		#end for
		return True

	def spawnEnemy(self,slot):
		e=Enemy()
		e.initialize(self.appMain,self,random.randint(0,self.x-1),random.randint(300,900),random.randint(1,self.appMain.getNumScreams()))
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
			self.log("Leveled up to %d! (Accuracy %.1f%%, with %d lives remaining)" % (self.level, self.player.hitPercentage, self.player.lives))
		else:
			self.log("Leveled up to %d! (Accuracy %.1f%%, with %d life remaining)" % (self.level, self.player.hitPercentage, self.player.lives))
	#end if 
		self.player.addScore(self.player.hitPercentage*self.player.hitPercentage*self.level*self.player.lives*0.5)
		self.levelupBonus.start(int(self.player.hitPercentage*0.1))
		self.level+=1
		self.enemies.append(None)
		self.nextLevelup=int(1+(self.level*self.level*0.3))

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
		self.score=0
		self.punches=0
		self.hits=0
		self.hitPercentage=0
		self.consecutiveHitBonus=BonusCounter()
		self.consecutiveHitBonus.initialize(self.appMain)
		self.consecutiveMissUnbonus=BonusCounter()
		self.consecutiveMissUnbonus.initialize(self.appMain)
		self.consecutiveHits=0
		self.consecutiveMisses=0

	def frameUpdate(self):
		self.consecutiveHitBonus.frameUpdate()
		self.consecutiveMissUnbonus.frameUpdate()
		if self.punching is False and self.appMain.wnd.keyPressed(window.K_SPACE): self.punchLaunch()
		if self.punching is True and self.punchTimer.elapsed>=self.punchHitTime: self.punchHit()
		if self.x!=0 and self.appMain.wnd.keyPressed(window.K_LEFT): self.moveTo(self.x-1)
		if self.x!=self.field.getX()-1 and self.appMain.wnd.keyPressed(window.K_RIGHT): self.moveTo(self.x+1)

	def punchLaunch(self):
		self.punches+=1
		self.punching=True
		s=sound()
		s.load(self.appMain.sounds["fists.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(90,110)
		s.play()
		self.punchTimer.restart()

	def punchHit(self):
		self.punching=False
		hit=False
		for elem in self.field.enemies:
			if elem.state==ENEMY_STATE_ALIVE and self.x==elem.x and elem.y<=self.punchRange:
				elem.hit()
				score=(1000-elem.speed)*(elem.y+1)*(0.5+(0.5*self.field.level))*0.1
				self.field.log("Hit! (speed %d, distance %d)" % (900-elem.speed, elem.y))
				self.addScore(score)
				hit=True
				self.hits+=1
				self.consecutiveHits+=1
				self.processConsecutiveMisses()
				self.calcHitPercentage()#penetration would higher the percentage, but I don't care
				self.field.logDefeat()
				break
			#end if
		#end for
		if not hit: self.punchMiss()
	#end punchHit

	def punchMiss(self):
		self.consecutiveMisses+=1
		if self.hits>0: self.calcHitPercentage()
		self.processConsecutiveHits()

	def processConsecutiveHits(self):
		if self.consecutiveHits>5:
			self.field.log("%d consecutive hits bonus!" % self.consecutiveHits)
			self.addScore(self.consecutiveHits*self.consecutiveHits*self.field.level*self.field.level)
			self.consecutiveHitBonus.start(self.consecutiveHits)
		#end if
		self.consecutiveHits=0

	def processConsecutiveMisses(self):
		if self.consecutiveMisses>5:
			self.field.log("%d consecutive misses penalty!" % self.consecutiveMisses)
			self.addScore(self.consecutiveMisses*self.consecutiveMisses*self.field.level*self.field.level*-1)
			self.consecutiveMissUnbonus.start(self.consecutiveMisses*-1)
		#end if
		self.consecutiveMisses=0

	def calcHitPercentage(self):
		self.hitPercentage=self.hits/self.punches*100
	def moveTo(self,p):
		self.x=p
		s=sound()
		s.load(self.appMain.sounds["change.ogg"])
		s.pan=self.field.getPan(self.x)
		s.play()

	def hit(self):
		self.lives-=1
		self.field.log("You've been slapped! (%d HP remaining)" % self.lives)
		s=sound()
		if self.lives>0:
			s.load(self.appMain.sounds["attacked.ogg"])
			s.play()
		else:
			s.load(self.appMain.sounds["gameover.ogg"])
			s.volume=-10
			s.play()

	def addScore(self,score):
		self.score+=score
		which="added"
		if score<=0: which="subtracted"
		self.field.log("Point: %.1f %s (%.1f)" % (score, which, self.score))
#end class Player

class Enemy():
	def __init__(self):
		self.scream=None
		self.bodyfall=None

	def __del__(self):
		self.field=None
		if self.scream is not None: self.scream.stop()
		if self.bodyfall is not None: self.bodyfall.stop()

	def initialize(self,appMain,field,x,speed,screamNum):
		self.appMain=appMain
		self.field=field
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
		self.field.player.hit()
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

class BonusCounter():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,appMain):
		self.appMain=appMain
		self.active=False
		self.countTimer=window.Timer()
		self.number=0
		self.current=0
	def start(self,number):
		if number==0: return
		self.number=number
		self.current=0
		self.countTimer.restart()
		self.active=True
		self.count()
	def frameUpdate(self):
		if self.active is True and self.countTimer.elapsed>=self.nextCountTime: self.count()
	def count(self):
		s=sound()

		if self.number>0:
			self.current+=1
			s.load(self.appMain.sounds["bonus.ogg"])
			p=75+(self.current*5)
			if p>300: p=300
		else:
			self.current-=1
			s.load(self.appMain.sounds["unbonus.ogg"])
			p=150+(self.current*3)
			if p<50: p=50
		#end if
		s.pitch=p
		s.play()
		if self.current==self.number:
			self.active=False
			return
		w=200-(abs(self.current)*10)
		if w<50: w=50
		self.nextCountTime=w
		self.countTimer.restart()

class GameResult:
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,field):
		self.score=field.player.score
		self.hitPercentage=field.player.hitPercentage
		self.hits=field.player.hits
		self.punches=field.player.punches
		self.level=field.level

class GameOptions:
	def __init__(self):
		self.BGMVOLUME_NEGATIVE_BOUNDARY=-30
		self.BGMVOLUME_POSITIVE_BOUNDARY=0
		self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY=-100
		self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY=-20
		self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY=20
		self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY=100

	def __del__(self):
		pass

	def initialize(self,importer):
		if isinstance(importer,GameOptions):
			self.copyFrom(importer)
		elif isinstance(importer,str):
			self.load(importer)
		else:
			self.setDefault()

	def setDefault(self):
		self.bgmVolume=-10
		self.leftPanningLimit=-100
		self.rightPanningLimit=100

	def copyFrom(self,importer):
		self.bgmVolume=importer.bgmVolume
		self.leftPanningLimit=importer.leftPanningLimit
		self.rightPanningLimit=importer.rightPanningLimit

	def load(self,filename):
		if os.path.isfile(filename) is not True:
			self.setDefault()
			self.save("data/options.dat")
			return False
		with open("data/options.dat", mode='r') as f:
			values=f.read().split("#")
		#end with
		self.bgmVolume=int(values[0])
		if self.bgmVolume<self.BGMVOLUME_NEGATIVE_BOUNDARY: self.bgmVolume=self.BGMVOLUME_NEGATIVE_BOUNDARY
		if self.bgmVolume>self.BGMVOLUME_POSITIVE_BOUNDARY: self.bgmVolume=self.BGMVOLUME_POSITIVE_BOUNDARY
		self.leftPanningLimit=int(values[1])
		if self.leftPanningLimit<self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY: self.leftPanningLimit=self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY
		if self.leftPanningLimit>self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY: self.leftPanningLimit=self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY
		self.rightPanningLimit=int(values[2])
		if self.rightPanningLimit>self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY: self.rightPanningLimit=self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY
		if self.rightPanningLimit<self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY: self.rightPanningLimit=self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY
		return True

	def save(self,filename):
		s="%d#%d#%d" % (self.bgmVolume,self.leftPanningLimit,self.rightPanningLimit)
		with open("data/options.dat", mode="w") as f:
			f.write(s)

class Item():
	def __init__(self):
		self.fallingBeep=None
		self.break=None

	def __del__(self):
		self.field=None
		if self.fallingBeep is not None: self.fallingBeep.stop()
		if self.break is not None: self.break.stop()

	def initialize(self,appMain,field,x,speed):
		self.appMain=appMain
		self.field=field
		self.x=x
		self.y=field.getY()
		self.speed=speed
		self.state=ITEM_STATE_ALIVE
		self.stepTimer=window.Timer()
		self.fallingBeep=sound()
		self.fallingBeep.load(appMain.sounds["itemfalling.ogg"])
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.fallingBeep.loop()

	def frameUpdate(self):
		if self.state==ITEM_STATE_BROKEN and self.break.playing is False: self.switchState(ITEM_STATE_SHOULDBEDELETED)
		if self.state==ENEMY_STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		self.state=newState
		if newState==ENEMY_STATE_BROKEN: self.playBroken()

	def step(self):
		if self.hitCheck() is True: return
		self.y-=1
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		s.play()
		self.stepTimer.restart()

	def hitCheck(self):
		if self.y!=0: return False
		self.switchState(ITEM_STATE_BROKEN)
		return True

	def hit(self):
		s=sound()
		s.load(self.appMain.sounds["itemget.ogg"])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.play()
		self.fallingBeep.stop()
		self.switchState(ITEM_STATE_SHOULDBEDELETED)

	def playBroken(self):
		self.break=sound()
		self.break.load(self.appMain.sounds["item_destroy%d.ogg" % random.randint(1,2)])
		self.break.pitch=random.randint(70,130)
		self.break.pan=self.field.getPan(self.x)
		self.break.volume=self.field.getVolume(self.y)
		self.break.play()
