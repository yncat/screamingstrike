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
import bgtsound
import bonusCounter
import enemy
import gameField
import gameModes
import gameOptions
import gameResult
import globalVars
import item
import itemConstants
import player

# constants
GAME_RESULT_TERMINATE = 0


class ssAppMain():
	"""
	The game's main application class.

	Instantiate this class, call initialize method, then call run method to start the application. Other methods are internally used and should not be called from outside of the class.
	"""
	def __init__(self):
		pass

	def __del__(self):
		pass

	def initialize(self):
		"""
		Initializes the app. returns True on success or False on failure.
		"""
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
		self.music = bgtsound.sound()
		self.music.stream("data/sounds/stream/bg.ogg")
		self.music.volume = self.options.bgmVolume
		self.numScreams = len(glob.glob("data/sounds/scream*.ogg"))
		return ret

	def initTranslation(self):
		"""
		Initializes translation.
		"""
		self.translator = gettext.translation("messages", "locale", languages=[self.options.language], fallback=True)
		self.translator.install()

	def resetItemVoice(self):
		"""
		Resets the speaker voice settings. This function searches voices and set the first found one as default. If no voice is available, it disables item speaking.
		"""
		if len(self.itemVoices)==0:
			self.options.itemVoice=""
		else:
			self.options.itemVoice=self.itemVoices[0]

	def getItemVoicesList(self):
		"""
		Searches for available voices as item speaker. It returns detected voice names as a list.

		:rtype: list
		"""
		lst=[]
		for elem in glob.glob("data/voices/*"):
			if os.path.isdir(elem): lst.append(os.path.basename(elem))
		return lst

	def getLocalesList(self):
		"""
		Searches for available languages. Returns the list of found languages.

		:rtype: list
		"""
		lst=[]
		for elem in glob.glob("locale/*"):
			if os.path.isdir(elem): lst.append(os.path.basename(elem))
		return lst

	def loadSounds(self):
		"""Preloads ingame sounds into memory. This is for enhancing performance while playing the game. """
		self.sounds={}
		files=glob.glob("data/sounds/*.ogg")
		for elem in files:
			self.sounds[os.path.basename(elem)]=sound_lib.sample.Sample(elem)
	# end loadSounds

	def getNumScreams(self):
		"""
		Returns the number of auto-detected screams.

		:rtype: int
		"""
		return self.numScreams

	def intro(self):
		"""Plays the intro sound. It blocks when the sound is playing, then starts the game music. """
		introsound=bgtsound.sound()
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
		"""
		Shows the main menu and returns what was selected as index.

		:rtype: int
		"""
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
		"""
		Starts the game. initialize method must be successfully called prior to call this method. It returns when the game is exited.
		"""
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
			self.resetMusicPitch()
			if self.resultScreen(result) is False: return

	def optionsMenu(self):
		"""Shows the game options menu. It returns when the menu is closed and all required i/o is finished."""
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
		"""Changes a specific game option. Used in the optionsMenu method.

		:param cursor: the cursor position in the settings menu
		:type cursor: int
		:param direction: Which arrow key was pressed (0=left / 1=right)
		:type direction: int
		"""
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
			s=bgtsound.sound()
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
			s=bgtsound.sound()
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
		"""
		Starts the gameplay. It returns when the gameplay is finished or exited. If it is finished with a result, returns the result. Otherwise, returns None.

		:rtype: gameResult.GameResult
		"""
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
		s=bgtsound.sound()
		s.load(self.sounds["dead.ogg"])
		s.pitch=random.randint(70,130)
		s.play()
		if self.wnd.wait(800)==False: return GAME_RESULT_TERMINATE
		with open("result.txt", mode='a') as f:
			f.write(field.exportLog())
		r=gameResult.GameResult()
		r.initialize(field)
		return r

	def resultScreen(self,result):
		"""Shows the game results screen."""
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

	def changeMusicPitch_relative(self,p):
		"""
		Changes the game music's pitch relatively. Positive values will increase (speedup), and negative values will decrease (slow down). If it hits either of the boundaries (50 lowest, 400 highest), this method does nothing.

		:param p: Amount
		:type p: int
		"""
		if self.music.pitch+p>400: return
		self.music.pitch+=p
	#end changeMusicPitch_relative

	def resetMusicPitch(self):
		"""
		Resets the music's pitch to default. The pitch change will be processed gradually and this method returns when the music is reverted to the normal speed.
"""
		while(True):
			if abs(self.music.pitch-100)<=2: break
			if self.music.pitch<100:
				self.music.pitch+=2
			else:
				self.music.pitch-=2
			self.wnd.wait(50)
		#end while
		self.music.pitch=100
	#end resetMusicPitch

# end class ssAppMain

