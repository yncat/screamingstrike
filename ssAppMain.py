# -*- coding: utf-8 -*-
# Screaming Strike main implementation
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import random
import glob
import os
import threading
import gettext
import window
import sound_lib.sample
from bgtsound import *
import bonusCounter
import enemy
import gameField
import gameModes
import gameOptions
import globalVars
import item
import itemConstants
import player

# constants
GAME_RESULT_TERMINATE = 0


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
		m.initialize(self.wnd,_("Main menu. Use your up and down arrows to choose an option, then press enter to confirm"),_("Normal mode#Arcade mode#Classic mode#Options#Exit"),self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
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
			if selected is False or selected==4: return
			if selected==3:
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
		self.wnd.say(_("%(playmode)s, start!") % {"playmode": gameModes.NAME_STR[mode]})
		field=gameField.GameField()
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

