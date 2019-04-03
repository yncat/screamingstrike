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
import bonusCounter
import enemy
import gameOptions
import globalVars
import player

# constants
MODE_NORMAL = 0
MODE_ARCADE = 1
MODEVAL_2_STR = ["Normal", "Arcade"]
GAME_RESULT_TERMINATE = 0
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


class ssAppMain():
	def __init__(self):
		pass

	def __del__(self):
		pass

	def initialize(self):
		"""Initializes the app. returns True on success or False on failure. """
		globalVars.appMain = self
		self.thread_loadSounds = threading.Thread(target=self.loadSounds)
		self.thread_loadSounds.setDaemon(True)
		self.thread_loadSounds.start()
		self.options = gameOptions.GameOptions()
		self.options.initialize("data/options.dat")
		self.itemVoices=self.getItemVoicesList()
		self.locales=self.getLocalesList()
		self.initTranslation()
		self.wnd = window.singletonWindow()
		ret = self.wnd.initialize(640, 480, "Screaming Strike!")
		self.music = sound()
		self.music.stream("data/sounds/stream/bg.ogg")
		self.music.volume = self.options.bgmVolume
		self.numScreams = len(glob.glob("data/sounds/scream*.ogg"))
		return ret

	def initTranslation(self):
		self.translator = gettext.translation("messages", "locale", languages=[self.options.language], fallback=True)
		self.translator.install()

	def resetItemVoice(self):
		if len(self.itemVoices)==0:
			self.options.itemVoice=""
		else:
			self.options.itemVoice=self.itemVoices[0]

	def getItemVoicesList(self):
		lst=[]
		for elem in glob.glob("data/voices/*"):
			if os.path.isdir(elem): lst.append(os.path.basename(elem))
		return lst

	def getLocalesList(self):
		lst=[]
		for elem in glob.glob("locale/*"):
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
		backup=gameOptions.GameOptions()
		backup.initialize(self.options)
		m=window.menu()
		m.initialize(self.wnd,_("Options Menu, use your up and down arrows to choose an option, left and right arrows to change values, enter to save or escape to discard changes"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.add(_("Background music volume"))
		m.add(_("Left panning limit"))
		m.add(_("Right panning limit."))
		m.add(_("Item announcement voice"))
		m.add(_("Language (restart to apply)"))
		m.open()
		while(True):
			if self.wnd.frameUpdate() is False: return False
			ret=m.frameUpdate()
			if self.wnd.keyPressed(window.K_LEFT): self.optionChange(m.getCursorPos(),-1)
			if self.wnd.keyPressed(window.K_RIGHT): self.optionChange(m.getCursorPos(),1)
			if ret is None: continue
			if ret==-1: 
				self.options=gameOptions.GameOptions()
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
		if cursor==3:#item voice
			c=0
			for n in self.itemVoices:#which are we selecting?
				if self.options.itemVoice==n: break
				c+=1
			#detected the current option
			if direction==1 and c==len(self.itemVoices)-1: return#clipping
			if direction==-1 and c==0: return#clipping
			c+=direction
			pl = ItemVoicePlayer()
			if not pl.initialize(self.itemVoices[c]):
				self.wnd.say(_("%(voice)s cannot be loaded.") % {"voice": self.itemVoices[c]})
				return
			self.wnd.say(self.itemVoices[c])
			pl.test()
			self.options.itemVoice=self.itemVoices[c]
			return
		#end item voices
		if cursor==4:#language
			c=0
			for n in self.locales:#which are we selecting?
				if n==self.options.language: break
				c+=1
			#detected the current option
			if direction==1 and c==len(self.locales)-1: return#clipping
			if direction==-1 and c==0: return#clipping
			c+=direction
			self.wnd.say(self.locales[c])
			self.options.language=self.locales[c]
			return
		#end item voices

	# end optionChange

	def gamePlay(self,mode):
		self.wnd.say(_("%(playmode)s, start!") % {"playmode": MODEVAL_2_STR[mode]})
		field=GameField()
		field.initialize(3,20,mode,self.options.itemVoice)
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
		self.items
		self.player=player.Player()
		self.player.initialize(self)
		self.defeats=0
		self.nextLevelup=2
		self.levelupBonus=bonusCounter.BonusCounter()
		self.levelupBonus.initialize()
		self.destructing=False
		self.destructTimer=window.Timer()
		self.itemVoicePlayer=ItemVoicePlayer()
		self.itemVoicePlayer.initialize(voice)


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
			if self.enemies[i] is not None and self.enemies[i].state==enemy.STATE_SHOULDBEDELETED: self.enemies[i]=None
			if self.enemies[i] is not None: self.enemies[i].frameUpdate()
			if self.enemies[i] is None: self.spawnEnemy(i)
		# end for
		for elem in self.items[:]:
			if elem is not None and elem.state==ITEM_STATE_SHOULDBEDELETED: self.items.remove(elem)
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
		self.fallingBeep.load(globalVars.appMain.sounds["itemfalling.ogg"])
		self.fallingBeep.pan=self.field.getPan(self.x)
		self.fallingBeep.volume=self.field.getVolume(self.y)
		self.fallingBeep.pitch=self.field.getPitch(self.y)
		self.fallingBeep.play_looped()
		self.type=type
		self.identifier=identifier

	def frameUpdate(self):
		if self.state==ITEM_STATE_BROKEN and self.shatter.playing is False: self.switchState(ITEM_STATE_SHOULDBEDELETED)
		if self.state==enemy.STATE_ALIVE and self.stepTimer.elapsed>=self.speed: self.step()

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
		s.load(globalVars.appMain.sounds["hit.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(70,130)
		s.play()
		s=sound()
		s.load(globalVars.appMain.sounds["itemget.ogg"])
		s.pan=self.field.getPan(self.x)
		s.volume=self.field.getVolume(self.y)
		s.play()
		self.field.itemVoicePlayer.play("get %s.ogg" % ITEM_NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.fallingBeep.stop()
		self.switchState(ITEM_STATE_SHOULDBEDELETED)

	def destroy(self):
		self.field.log(_("A \"%(item)s\" item was shattered into peaces by the destruction!") % {"item": ITEM_NAMES[self.type][self.identifier]})
		self.switchState(ITEM_STATE_BROKEN)

	def playShatter(self):
		self.field.itemVoicePlayer.play("lose %s.ogg" % ITEM_NAMES[self.type][self.identifier], self.field.getPan(self.x))
		self.shatter=sound()
		self.shatter.load(globalVars.appMain.sounds["item_destroy%d.ogg" % random.randint(1,2)])
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
		super().initialize(player,globalVars.appMain.sounds["shrink.ogg"],globalVars.appMain.sounds["shrinkFade.ogg"],"Shrink")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange*2)

class BlurredEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["blurred.ogg"],globalVars.appMain.sounds["blurredFade.ogg"],"Blurred")

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
		super().initialize(player,globalVars.appMain.sounds["slowDown.ogg"],globalVars.appMain.sounds["slowDownFade.ogg"],"Slow down")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

class MegatonPunchEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["megatonPunch.ogg"],globalVars.appMain.sounds["megatonPunchFade.ogg"],"Megaton punch")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange*5)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange/5)

class BoostEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["boost.ogg"],globalVars.appMain.sounds["boostFade.ogg"],"Boost")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

class PenetrationEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["penetration.ogg"],globalVars.appMain.sounds["penetrationFade.ogg"],"Penetration")

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

