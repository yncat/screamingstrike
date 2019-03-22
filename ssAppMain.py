# -*- coding: utf-8 -*-
# Screaming Strike main implementation
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
import glob
import os
import threading
import datetime
import gettext
import window
import sound_lib.sample
from bgtsound import *
# constants
MODE_NORMAL = 0
MODE_ARCADE = 1
MODEVAL_2_STR = ["Normal", "Arcade"]
GAME_RESULT_TERMINATE = 0
ENEMY_STATE_ALIVE = 0
ENEMY_STATE_SCREAMING = 1
ENEMY_STATE_FALLING = 2
ENEMY_STATE_SHOULDBEDELETED = 3
ITEM_STATE_ALIVE = 0
ITEM_STATE_BROKEN = 1
ITEM_STATE_SHOULDBEDELETED = 2

ITEM_BASE_EFFECT_TIME = 15000
ITEM_TYPE_NASTY = 0
ITEM_TYPE_GOOD = 1

ITEM_NASTY_SHRINK = 0
ITEM_NASTY_BLURRED = 1
ITEM_NASTY_SLOWDOWN = 2
ITEM_NASTY_MAX = 2

ITEM_GOOD_MEGATONPUNCH = 0
ITEM_GOOD_BOOST = 1
ITEM_GOOD_PENETRATION = 2
ITEM_GOOD_DESTRUCTION = 3
ITEM_GOOD_EXTRALIFE = 4
ITEM_GOOD_MAX = 4
ITEM_NAMES = {}
ITEM_NAMES[ITEM_TYPE_NASTY] = {ITEM_NASTY_SHRINK: "Shrink",
    ITEM_NASTY_BLURRED: "Blurred", ITEM_NASTY_SLOWDOWN: "Slow down"}
ITEM_NAMES[ITEM_TYPE_GOOD] = {ITEM_GOOD_MEGATONPUNCH: "Megaton punch", ITEM_GOOD_BOOST: "Boost",
    ITEM_GOOD_PENETRATION: "Penetration", ITEM_GOOD_DESTRUCTION: "Destruction", ITEM_GOOD_EXTRALIFE: "Extra life"}
PLAYER_DEFAULT_PUNCH_RANGE = 4
PLAYER_DEFAULT_PUNCH_SPEED = 200


class ssAppMain():
	def __init__(self):
		pass

	def __del__(self):
		pass

	def initialize(self):
		"""Initializes the app. returns True on success or False on failure. """
		global appMain
		appMain = self
		self.thread_loadSounds = threading.Thread(target=self.loadSounds)
		self.thread_loadSounds.setDaemon(True)
		self.thread_loadSounds.start()
		self.options = GameOptions()
		self.options.initialize("data/options.dat")
		self.initTranslation()
		self.wnd = window.singletonWindow()
		ret = self.wnd.initialize(640, 480, "Screaming Strike!")
		self.music = sound()
		self.music.stream("data/sounds/stream/bg.ogg")
		self.music.volume = self.options.bgmVolume
		self.numScreams = len(glob.glob("data/sounds/scream*.ogg"))
		self.itemVoicePlayer = ItemVoicePlayer()
		print(self.getItemVoicesList())
		if not self.itemVoicePlayer.initialize(
		    self.options.itemVoice): self.resetItemVoice()
		return ret

	def initTranslation(self):
		self.translator = gettext.translation("messages", "locale", languages=[
                                      "ja-JP"], fallback=True)
		self.translator.install()

	def resetItemVoice(self):
		voices=self.getItemVoicesList()
		if len(voices)==0:
			self.options.itemVoice=""
		else:
			self.options.itemVoice=voices[0]

	def getItemVoicesList(self):
		lst=[]
		for elem in glob.glob("data/voices/*"):
			if os.path.isdir(elem): lst.append(os.path.basename(elem))
		return lst

	def loadSounds(self):
		"""Preload ingame sounds into memory. This is for enhancing performance while playing the game. """
		self.sounds={}
		files=glob.glob("data/sounds/*.ogg")
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
	# end loadSounds

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
			# end skipping with enter
		# end while intro is playing
		self.thread_loadSounds.join()
		self.music.play_looped()
	# end intro

	def mainmenu(self):
		m=window.menu()
		m.initialize(self.wnd,_("Main menu. Use your up and down arrows to choose an option, then press enter to confirm"),_("Normal mode#Arcade mode#Options#Exit"),self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			if self.wnd.keyPressed(window.K_ESCAPE): return False
			selected=m.frameUpdate()
			if selected is not None and selected>=0: return selected
		# end loop
	# end mainmenu

	def run(self):
		if self.intro() is False: return
		while(True):
			selected=self.mainmenu()
			if selected is False or selected==3: return
			if selected==2:
				if self.optionsMenu() is False: return
				continue
			# end if
			result=self.gamePlay(selected)
			if result==GAME_RESULT_TERMINATE: return
			if self.resultScreen(result) is False: return

	def optionsMenu(self):
		backup=GameOptions()
		backup.initialize(self.options)
		m=window.menu()
		m.initialize(self.wnd,_("Options Menu, use your up and down arrows to choose an option, left and right arrows to change values, enter to save or escape to discard changes"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.add(_("Background music volume"))
		m.add(_("Left panning limit"))
		m.add(_("Right panning limit."))
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
				self.wnd.say(_("Changes discarded."))
				self.music.volume=self.options.bgmVolume
				return True
			# end if
			if ret>=0:
				self.wnd.say(_("Settings saved"))
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
		# end bgm volume
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
	# end left panning limit
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
		# end left panning limit
	# end optionChange

	def gamePlay(self,mode):
		self.wnd.say(_("%(playmode)s, start!") % {"playmode": MODEVAL_2_STR[mode]})
		field=GameField()
		field.initialize(3,20,mode)
		field.setLimits(self.options.leftPanningLimit,self.options.rightPanningLimit)
		while(True):
			if self.wnd.frameUpdate() is False: return GAME_RESULT_TERMINATE
			if self.wnd.keyPressed(window.K_ESCAPE): return GAME_RESULT_TERMINATE
			if field.frameUpdate() is False:break
		# end while
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
		m.initialize(self.wnd,_("Game result"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.add(_("Final score: %(score)d") % {"score": result.score})
		m.add(_("Punches: %(punches)d, hits: %(hits)d, accuracy: %(accuracy).2f%%") % {"punches": result.punches, "hits": result.hits, "accuracy": result.hitPercentage})
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			r=m.frameUpdate()
			if r is not None:break
		# end while
		return True



# end class ssAppMain

class GameField():
	def __init__(self):
		pass
	def __del__(self):
		self.Enemies=None
		self.player=None

	def initialize(self, x,y,mode):
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
		self.items
		self.player=Player()
		self.player.initialize(self)
		self.defeats=0
		self.nextLevelup=2
		self.levelupBonus=BonusCounter()
		self.levelupBonus.initialize()
		self.destructing=False
		self.destructTimer=window.Timer()
		self.logs=[]
		self.log(_("Game started at %(startedtime)s!") % {"startedtime": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")})

	def setModeHandler(self,mode):
		if mode==MODE_NORMAL:
			self.modeHandler=NormalModeHandler()
		elif mode==MODE_ARCADE:
			self.modeHandler=ArcadeModeHandler()
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
			if self.enemies[i] is not None and self.enemies[i].state==ENEMY_STATE_SHOULDBEDELETED: self.enemies[i]=None
			if self.enemies[i] is not None: self.enemies[i].frameUpdate()
			if self.enemies[i] is None: self.spawnEnemy(i)
		# end for
		for elem in self.items[:]:
			if elem is not None and elem.state==ITEM_STATE_SHOULDBEDELETED: self.items.remove(elem)
			if elem is not None: elem.frameUpdate()
		return True

	def spawnEnemy(self,slot):
		e=Enemy()
		e.initialize(self,random.randint(0,self.x-1),random.randint(300,900),random.randint(1,appMain.getNumScreams()))
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
			self.log(_("Leveled up to %(newlevel)! (Accuracy %(accuracy).1f%%, with %(lives)d lives remaining)") % {"newlevel": self.level, "accuracy": self.player.hitPercentage, "lives": self.player.lives})
		else:
			self.log(_("Leveled up to %(newlevel)d! (Accuracy %(accuracy).1f%%, with %(lives)d life remaining)") % {"newlevel": self.level, "accuracy": self.player.hitPercentage, "lives": self.player.lives})
	# end if 
		self.player.addScore(self.player.hitPercentage*self.player.hitPercentage*self.level*self.player.lives*0.5)
		self.levelupBonus.start(int(self.player.hitPercentage*0.1))
		self.level+=1
		self.enemies.append(None)
		self.nextLevelup=int(1+(self.level*self.level*0.25))

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
		playOneShot(appMain.sounds["destructPowerup.ogg"])
		self.destructTimer.restart()
		self.destructing=True

	def performDestruction(self):
		playOneShot(appMain.sounds["destruct.ogg"])
		self.log(_("Activating destruction!"))
		for elem in self.enemies:
			if elem is not None and elem.state==ENEMY_STATE_ALIVE: elem.hit()
			self.logDefeat()
		for elem in self.items:
			elem.destroy()
		self.destructing=False
		self.log(_("End destruction!"))
# end class GameField

class Player():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,field):
		self.field=field
		self.lives=3
		self.x=field.getCenterPosition()
		self.punchTimer=window.Timer()
		self.punchTimer=window.Timer()
		self.punching=False
		self.punchSpeed=PLAYER_DEFAULT_PUNCH_SPEED
		self.punchRange=PLAYER_DEFAULT_PUNCH_RANGE
		self.score=0
		self.punches=0
		self.hits=0
		self.hitPercentage=0
		self.consecutiveHitBonus=BonusCounter()
		self.consecutiveHitBonus.initialize()
		self.consecutiveMissUnbonus=BonusCounter()
		self.consecutiveMissUnbonus.initialize()
		self.consecutiveHits=0
		self.consecutiveMisses=0
		self.itemEffects=[]
		self.penetrate=False

	def frameUpdate(self):
		self.consecutiveHitBonus.frameUpdate()
		self.consecutiveMissUnbonus.frameUpdate()
		if self.punching is False and appMain.wnd.keyPressed(window.K_SPACE): self.punchLaunch()
		if self.punching is True and self.punchTimer.elapsed>=self.punchSpeed: self.punchHit()
		if self.x!=0 and appMain.wnd.keyPressed(window.K_LEFT): self.moveTo(self.x-1)
		if self.x!=self.field.getX()-1 and appMain.wnd.keyPressed(window.K_RIGHT): self.moveTo(self.x+1)
		for elem in self.itemEffects[:]:
			if not elem.frameUpdate(): self.itemEffects.remove(elem)

	def punchLaunch(self):
		self.punches+=1
		self.punching=True
		s=sound()
		s.load(appMain.sounds["fists.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(90,110)
		s.play()
		self.punchTimer.restart()

	def punchHit(self):
		self.punching=False
		hit=0
		for pos in range(int(self.punchRange)+1):
			for elem in self.field.enemies:
				if elem.state==ENEMY_STATE_ALIVE and self.x==elem.x and elem.y==pos:
					elem.hit()
					hit+=1
					self.hits+=1
					self.consecutiveHits+=1
					self.processConsecutiveMisses()
					self.calcHitPercentage()#penetration would higher the percentage, but I don't care
					self.field.logDefeat()
					if not self.penetrate: break
				# end if
			# end for enemies
			if not self.penetrate and hit>0: break
			for elem in self.field.items:
				if elem.state==ITEM_STATE_ALIVE and self.x==elem.x and elem.y==pos:
					elem.hit()
					self.processItemHit(elem)
					hit=True
					self.hits+=1
					self.consecutiveHits+=1
					self.processConsecutiveMisses()
					self.calcHitPercentage()
					if not self.penetrate: break
				# end if
			# end for items
		# end for range
		if not hit: self.punchMiss()
	# end punchHit

	def punchMiss(self):
		self.consecutiveMisses+=1
		if self.hits>0: self.calcHitPercentage()
		self.processConsecutiveHits()

	def processConsecutiveHits(self):
		if self.consecutiveHits>5:
			self.field.log(_("%(hits)d consecutive hits bonus!") % {"hits": self.consecutiveHits})
			self.addScore(self.consecutiveHits*self.consecutiveHits*self.field.level*self.field.level)
			self.consecutiveHitBonus.start(self.consecutiveHits)
		# end if
		self.consecutiveHits=0

	def processConsecutiveMisses(self):
		if self.consecutiveMisses>5:
			self.field.log(_("%(misses)d consecutive misses penalty!") % {"misses": self.consecutiveMisses})
			self.addScore(self.consecutiveMisses*self.consecutiveMisses*self.field.level*self.field.level*-1)
			self.consecutiveMissUnbonus.start(self.consecutiveMisses*-1)
		# end if
		self.consecutiveMisses=0

	def processItemHit(self,item):
		if item.type==ITEM_TYPE_NASTY:
			self.processNastyItemHit(item)
		else:
			self.processGoodItemHit(item)

	def processNastyItemHit(self,item):
		if item.identifier==ITEM_NASTY_SHRINK:
			e=ShrinkEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if item.identifier==ITEM_NASTY_BLURRED:
			e=BlurredEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if item.identifier==ITEM_NASTY_SLOWDOWN:
			e=SlowDownEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return

	def processGoodItemHit(self,item):
		if item.identifier==ITEM_GOOD_MEGATONPUNCH:
			existing=self.findEffect("Megaton punch")
			if existing is None:
				e=MegatonPunchEffect()
				e.initialize(self)
				e.activate()
				self.itemEffects.append(e)
			else:
				existing.extend(ITEM_BASE_EFFECT_TIME)
			return
		if item.identifier==ITEM_GOOD_BOOST:
			e=BoostEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if item.identifier==ITEM_GOOD_PENETRATION:
			existing=self.findEffect("Penetration")
			if existing is None:
				e=PenetrationEffect()
				e.initialize(self)
				e.activate()
				self.itemEffects.append(e)
			else:
				existing.extend(ITEM_BASE_EFFECT_TIME)
			return
		if item.identifier==ITEM_GOOD_DESTRUCTION:
			self.field.startDestruction()
			return
		if item.identifier==ITEM_GOOD_EXTRALIFE:
			self.lives+=1
			self.field.log(_("Extra life! (now %(lives)d lives)") % {"lives": self.lives})
			s=sound()
			s.load(appMain.sounds["extraLife.ogg"])
			s.pitch=60+(self.lives*10)
			s.play()
			return

	def findEffect(self,name):
		for elem in self.itemEffects:
			if elem.name==name: return elem
		return None

	def setPunchRange(self,r):
		previous=self.punchRange
		self.field.log(_("The effective range of your Punch is now %(range)d (from %(from)d)") % {"range": r, "from": previous})
		self.punchRange=r

	def setPunchSpeed(self,s):
		previous=self.punchSpeed
		self.field.log(_("The speed of your punch is now %(speed)d milliseconds (from %(from)d)") % {"speed": s, "from": previous})
		self.punchSpeed=s

	def setPenetration(self,p):
		if p is True:
			self.field.log(_("Your punches now penetrate enemies and items!"))
		else:
			self.field.log(_("Your punches no longer penetrate enemies and items!"))
		self.penetration=p

	def calcHitPercentage(self):
		self.hitPercentage=self.hits/self.punches*100
	def moveTo(self,p):
		self.x=p
		s=sound()
		s.load(appMain.sounds["change.ogg"])
		s.pan=self.field.getPan(self.x)
		s.play()

	def hit(self):
		self.lives-=1
		self.field.log(_("You've been slapped! (%(lives)d HP remaining)") % {"lives": self.lives})
		s=sound()
		if self.lives>0:
			s.load(appMain.sounds["attacked.ogg"])
			s.play()
		else:
			s.load(appMain.sounds["gameover.ogg"])
			s.volume=-10
			s.play()

	def addScore(self,score):
		self.score+=score
		which=_("added")
		if score<=0: which=_("subtracted")
		self.field.log(_("Point: %(added).1f %(changestr)s (%(total).1f)") % {"added": score, "changestr": which, "total": self.score})
# end class Player

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
		if self.attackCheck() is True: return
		self.y-=1
		s=sound()
		num=0
		while True:
			num=random.randint(1,18)
			if num!=self.lastStepNum: break
		# end while
		s.load(appMain.sounds["s_lf%d.ogg" % num])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.pitch=random.randint(90,110)
		s.play()
		self.stepTimer.restart()

	def attackCheck(self):
		if self.y!=0: return False
		self.field.player.hit()
		self.switchState(ENEMY_STATE_SHOULDBEDELETED)
		return True

	def hit(self):
		s=sound()
		s.load(appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		self.playScream()
		self.switchState(ENEMY_STATE_SCREAMING)
		score=(1000-self.speed)*(self.y+1)*(0.5+(0.5*self.field.level))*0.1
		self.field.log(_("Hit! (speed %(speed)d, distance %(distance)d)") % {"speed": 900-self.speed, "distance": self.y})
		self.field.player.addScore(score)

	def playScream(self):
		self.scream=sound()
		self.scream.load(appMain.sounds["scream%d.ogg" % self.screamNum])
		self.scream.pitch=random.randint(80,120)
		self.scream.pan=self.field.getPan(self.x)
		self.scream.volume=self.field.getVolume(self.y)
		self.scream.play()

	def playBodyfall(self):
		self.bodyfall=sound()
		self.bodyfall.load(appMain.sounds["dead.ogg"])
		self.bodyfall.pitch=random.randint(70,130)
		self.bodyfall.pan=self.field.getPan(self.x)
		self.bodyfall.volume=self.field.getVolume(self.y)
		self.bodyfall.play()

class BonusCounter():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self):
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
			s.load(appMain.sounds["bonus.ogg"])
			p=75+(self.current*5)
			if p>300: p=300
		else:
			self.current-=1
			s.load(appMain.sounds["unbonus.ogg"])
			p=150+(self.current*3)
			if p<50: p=50
		# end if
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
		self.itemVoice="chris"
	def copyFrom(self,importer):
		self.bgmVolume=importer.bgmVolume
		self.leftPanningLimit=importer.leftPanningLimit
		self.rightPanningLimit=importer.rightPanningLimit
		self.itemVoice=importer.itemVoice

	def load(self,filename):
		if os.path.isfile(filename) is not True:
			self.setDefault()
			self.save("data/options.dat")
			return False
		with open("data/options.dat", mode='r') as f:
			values=f.read().split("#")
		# end with
		self.bgmVolume=int(values[0])
		if self.bgmVolume<self.BGMVOLUME_NEGATIVE_BOUNDARY: self.bgmVolume=self.BGMVOLUME_NEGATIVE_BOUNDARY
		if self.bgmVolume>self.BGMVOLUME_POSITIVE_BOUNDARY: self.bgmVolume=self.BGMVOLUME_POSITIVE_BOUNDARY
		self.leftPanningLimit=int(values[1])
		if self.leftPanningLimit<self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY: self.leftPanningLimit=self.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY
		if self.leftPanningLimit>self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY: self.leftPanningLimit=self.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY
		self.rightPanningLimit=int(values[2])
		if self.rightPanningLimit>self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY: self.rightPanningLimit=self.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY
		if self.rightPanningLimit<self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY: self.rightPanningLimit=self.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY
		self.itemVoice=values[3]
		return True

	def save(self,filename):
		s="%d#%d#%d#%s" % (self.bgmVolume,self.leftPanningLimit,self.rightPanningLimit,self.itemVoice)
		with open("data/options.dat", mode="w") as f:
			f.write(s)

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
		self.state=ITEM_STATE_ALIVE
		self.stepTimer=window.Timer()
		self.fallingBeep=sound()
		self.fallingBeep.load(appMain.sounds["itemfalling.ogg"])
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.fallingBeep.play_looped()
		self.type=type
		self.identifier=identifier

	def frameUpdate(self):
		if self.state==ITEM_STATE_BROKEN and self.shatter.playing is False: self.switchState(ITEM_STATE_SHOULDBEDELETED)
		if self.state==ENEMY_STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

	def switchState(self, newState):
		self.state=newState
		if newState==ITEM_STATE_BROKEN: self.playShatter()

	def step(self):
		if self.destroyCheck() is True: return
		self.y-=1
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.stepTimer.restart()

	def destroyCheck(self):
		if self.y!=0: return False
		self.switchState(ITEM_STATE_BROKEN)
		self.field.log(_("A \"%(item)s\" item fell on the ground and shattered into peaces!") % {"item": ITEM_NAMES[self.type][self.identifier]})
		return True

	def hit(self):
		self.field.log(_("Obtained a \"%(item)s\" item!") % {"item": ITEM_NAMES[self.type][self.identifier]})
		s=sound()
		s.load(appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		s=sound()
		s.load(appMain.sounds["itemget.ogg"])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.play()
		appMain.itemVoicePlayer.play("get %s.ogg" % ITEM_NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.fallingBeep.stop()
		self.switchState(ITEM_STATE_SHOULDBEDELETED)

	def destroy(self):
		self.field.log(_("A \"%(item)s\" item was shattered into peaces by the destruction!") % {"item": ITEM_NAMES[self.type][self.identifier]})
		self.switchState(ITEM_STATE_BROKEN)

	def playShatter(self):
		appMain.itemVoicePlayer.play("lose %s.ogg" % ITEM_NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.shatter=sound()
		self.shatter.load(appMain.sounds["item_destroy%d.ogg" % random.randint(1,2)])
		self.shatter.pitch=random.randint(70,130)
		self.shatter.pan=self.field.getPan(self.x)
		self.shatter.volume=self.field.getVolume(self.y)
		self.shatter.play()
		self.fallingBeep.stop()

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
		t=ITEM_TYPE_NASTY if random.randint(1,100)<=spd/10 else ITEM_TYPE_GOOD
		ident=random.randint(0,ITEM_NASTY_MAX) if t==ITEM_TYPE_NASTY else random.randint(0,ITEM_GOOD_MAX)
		i=Item()
		i.initialize(self.field,random.randint(0,self.field.x-1),spd,t,ident)
		self.field.items.append(i)
		self.resetItemComingTimer()

	def resetItemComingTimer(self):
		self.itemComingTimer.restart()
		self.itemComingTime=random.randint(0,60000)

class ItemEffectBase(object):
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,player,onSound,offSound,name):
		self.player=player
		self.active=False
		self.timer=window.Timer()
		self.onSound=onSound
		self.offSound=offSound
		self.lasts=ITEM_BASE_EFFECT_TIME
		self.name=name

	def activate(self):
		s=sound()
		s.load(self.onSound)
		s.play()
		self.active=True
		self.timer.restart()
		self.player.field.log(_("A new \"%(item)s\" effect is starting!") % {"item": self.name})

	def deactivate(self):
		s=sound()
		s.load(self.offSound)
		s.play()
		self.active=False
		self.player.field.log(_("One of your \"%(item)s\" effects is ending!") % {"item": self.name})

	def extend(self,ms):
		s=sound()
		s.load(self.onSound)
		s.pitch=130
		s.play()
		self.lasts+=ms
		self.player.field.log(_("Your \"%(item)s\" effect has been extended for %(extended)d milliseconds! (now %(newtime)d)") %  {"item": self.name, "extended": ms, "newtime": self.lasts-self.timer.elapsed})

	def frameUpdate(self):
		if self.active is not True: return False
		if self.timer.elapsed>=self.lasts:
			self.deactivate()
			return False
		return True

class ShrinkEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["shrink.ogg"],appMain.sounds["shrinkFade.ogg"],"Shrink")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange*2)

class BlurredEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["blurred.ogg"],appMain.sounds["blurredFade.ogg"],"Blurred")

	def frameUpdate(self):
		if super().frameUpdate() is False: return False
		if random.randint(1,10)==1:
			while(True):
				d=random.randint(0,self.player.field.getX()-1)
				if d!=self.player.x: break
			# end while
			self.player.moveTo(d)
		# whether to trigger blurring?
		return True
	# end frameUpdate

class SlowDownEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["slowDown.ogg"],appMain.sounds["slowDownFade.ogg"],"Slow down")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

class MegatonPunchEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["megatonPunch.ogg"],appMain.sounds["megatonPunchFade.ogg"],"Megaton punch")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange*5)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange/5)

class BoostEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["boost.ogg"],appMain.sounds["boostFade.ogg"],"Boost")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

class PenetrationEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,appMain.sounds["penetration.ogg"],appMain.sounds["penetrationFade.ogg"],"Penetration")

	def activate(self):
		super().activate()
		self.player.setPenetration(True)

	def deactivate(self):
		super().deactivate()
		self.player.setPenetration(False)

class ItemVoicePlayer():
	def __init__(self):
		pass
	def __del__(self):
		pass

	def initialize(self,name):
		self.active=False
		if not os.path.exists("data/voices/%s" % name): return False
		self.sounds={}
		files=glob.glob("data/voices/%s/*.ogg" % name)
		if len(files)==0: return False
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
		self.name=name
		self.active=True

	def clear(self):
		self.sounds={}

	def test(self):
		if not self.active: return
		playOneShot(random.choice(list(self.sounds)))

	def play(self,file, pan):
		if not self.active: return
		if file in self.sounds:
			s=sound()
			s.load(self.sounds[file])
			s.pan=pan
			s.play()

