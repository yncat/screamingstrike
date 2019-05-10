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
import gameField
import gameModes
import gameOptions
import gameResult
import globalVars
import highscore
import scorePostingAdapter
import collection

COLLECTION_DATA_FILENAME="data/collection.dat"
HIGHSCORE_DATA_FILENAME="data/highscore.dat"

class ssAppMain(window.SingletonWindow):
	"""
	The game's main application class.

	Instantiate this class, call initialize method, then call run method to start the application. Other methods are internally used and should not be called from outside of the class.
	"""
	def __init__(self):
		super().__init__()

	def __del__(self):
		super().__del__()

	def initialize(self):
		"""
		Initializes the app. returns True on success or False on failure.

		:rtype: bool
		"""
		super().initialize(640, 480, "Screaming Strike!")
		globalVars.appMain = self
		self.thread_loadSounds = threading.Thread(target=self.loadSounds)
		self.thread_loadSounds.setDaemon(True)
		self.thread_loadSounds.start()
		self.options = gameOptions.GameOptions()
		self.options.initialize("data/options.dat")
		self.itemVoices=self.getItemVoicesList()
		self.locales=self.getLocalesList()
		self.initTranslation()
		self.music = bgtsound.sound()
		self.music.stream("data/sounds/stream/bg.ogg")
		self.music.volume = self.options.bgmVolume
		self.numScreams = len(glob.glob("data/sounds/scream*.ogg"))
		self.collectionStorage=collection.CollectionStorage()
		self.collectionStorage.initialize(self.numScreams,COLLECTION_DATA_FILENAME)
		self.hsStorage=highscore.HsStorage()
		self.hsStorage.initialize(HIGHSCORE_DATA_FILENAME)
		return True

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
			self.frameUpdate()
			if self.keyPressed(window.K_RETURN):
				introsound.fadeout(900)
				self.wait(1000)
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
		m.initialize(self,_("Main menu. Use your up and down arrows to choose an option, then press enter to confirm"),None,self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.append(_("Normal mode")+"&1")
		m.append(_("Arcade mode")+"&2")
		m.append(_("Classic mode")+"&3")
		m.append(_("Collection")+"&C")
		m.append(_("Erase data")+"&E")
		m.append(_("Options")+"&o")
		m.append(_("Quit")+"&Q")

		m.open()
		while(True):
			self.frameUpdate()
			if self.keyPressed(window.K_ESCAPE): return False
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
			if selected is False or selected==6: self.exit()
			if selected==3:
				self.collectionDialog()
				continue
			if selected==4:
				self.eraseDataDialog()
				continue
			#end erase data
			if selected==5:
				self.optionsDialog()
				continue
			#end options
			self.play(selected)
		#end while
	#end run

	def play(self,mode):
		"""Plays the specified mode.

		:param mode: Mode in number.
		:type mode: int
		"""
		result=self.gamePlay(mode)
		self.resetMusicPitch()
		self.reviewCollection(result)
		self.resultScreen(result)
		if result.score>0:
			self.scorePostDialog(result)

	def collectionDialog(self):
		"""Shows the collection dialog. Returns when user pressed escape and left the dialog."""
		c=collection.CollectionDialog()
		c.run(self)

	def eraseDataDialog(self):
		"""Shows the erase data dialog. Returns when user leaves this menu."""
		m=window.menu()
		m.initialize(self,_("Select the data to irase"),[_("Highscores"),_("Collections"),_("Back")],self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.open()
		while(True):
			self.frameUpdate()
			r=m.frameUpdate()
			if r is None: continue
			if r==-1 or m.isLast(r): break
			if not self.keyPressing(window.K_LSHIFT) and not self.keyPressing(window.K_RSHIFT):
				self.say(_("Hold shift and enter to erase."))
				continue
			#end confirmation
			if r==0:
				self.hsStorage.reset()
				self.say(_("Your highscores are all reset!"))
				continue
			if r==1:
				self.collectionStorage.reset()
				self.say(_("Your collections are all reset!"))
				continue
			#end what to reset
		#end while
	#end eraseDataDialog

	def optionsDialog(self):
		"""Shows the game options menu. It returns when the menu is closed and all required i/o is finished."""
		backup=gameOptions.GameOptions()
		backup.initialize(self.options)
		m=window.menu()
		m.initialize(self,_("Options Menu, use your up and down arrows to choose an option, left and right arrows to change values, enter to save or escape to discard changes"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.append(_("Background music volume"))
		m.append(_("Left panning limit"))
		m.append(_("Right panning limit."))
		m.append(_("Item announcement voice"))
		m.append(_("Language (restart to apply)"))
		m.open()
		while(True):
			self.frameUpdate()
			ret=m.frameUpdate()
			if self.keyPressed(window.K_LEFT): self.optionChange(m.getCursorPos(),-1)
			if self.keyPressed(window.K_RIGHT): self.optionChange(m.getCursorPos(),1)
			if ret is None: continue
			if ret==-1: 
				self.options=gameOptions.GameOptions()
				self.options.initialize(backup)
				self.say(_("Changes discarded."))
				self.music.volume=self.options.bgmVolume
				return True
			# end if
			if ret>=0:
				self.say(_("Settings saved"))
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
			self.say("%d" % (abs(-30-self.options.bgmVolume)*0.5))
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
				self.say(_("%(voice)s cannot be loaded.") % {"voice": self.itemVoices[c]})
				return
			self.say(self.itemVoices[c])
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
			self.say(self.locales[c])
			self.options.language=self.locales[c]
			return
		#end item voices

	# end optionChange

	def gamePlay(self,mode):
		"""
		Starts the gameplay. It returns when the gameplay is finished or exited. If it is finished with a result, returns the result. Otherwise, returns None.

		:rtype: gameResult.GameResult
		"""
		self.say(_("%(playmode)s, high score %(highscore)s, start!") % {"playmode": gameModes.ALL_MODES_STR[mode], "highscore":self.hsStorage.get(gameModes.ALL_MODES_STR[mode])})
		field=gameField.GameField()
		field.initialize(3,20,mode,self.options.itemVoice)
		field.setLimits(self.options.leftPanningLimit,self.options.rightPanningLimit)
		while(True):
			self.frameUpdate()
			if self.keyPressed(window.K_ESCAPE):
				result=gameResult.GameResult()
				result.initialize(field)
				result.aboated=True
				field.clear()
				return result
			#end aboat
			if field.frameUpdate() is False:break
		# end while
		field.clear()
		self.wait(2000)
		s=bgtsound.sound()
		s.load(self.sounds["dead.ogg"])
		s.pitch=random.randint(70,130)
		s.play()
		self.wait(800)
		with open("result.txt", mode='a') as f:
			f.write(field.exportLog())
		r=gameResult.GameResult()
		r.initialize(field)
		return r

	def reviewCollection(self,result):
		"""Shows unlocked collections, if any.

		:param result: result to look.
		:type result: gameResult.GameResult
		"""
		num=len(result.unlockedCollection)
		if num==0: return
		bgtsound.playOneShot(self.sounds["unlock.ogg"])
		self.wait(500)
		m=window.menu()
		s=_("collection") if num==1 else _("collections")
		m.initialize(self,_("Unlocked %(number)d %(collection)s!" % {"number": num, "collection": s}),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		for elem in result.unlockedCollection:
			m.append(str(elem))
		#end for
		m.append(_("Close"))
		m.open()
		while(True):
			self.frameUpdate()
			r=m.frameUpdate()
			if r is None:continue
			if r==-1 or m.isLast(r): break
			bgtsound.playOneShot(self.sounds["scream%s.ogg" % m.getString(m.getCursorPos())])
		#end while
	#end reviewCollection

	def resultScreen(self,result):
		"""Shows the game results screen."""
		m=window.menu()
		m.initialize(self,_("Game result"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.append(_("Final score: %(score)d") % {"score": result.score})
		if result.highscore is not None:
			m.append(_("New high score! Plus %(distance)d (last: %(last)d)") % {"distance": result.highscore-result.previousHighscore, "last": result.previousHighscore})
			bgtsound.playOneShot(self.sounds["highscore.ogg"])
			self.hsStorage.set(result.mode,result.highscore)
		#end if highscore
		m.append(_("Punches: %(punches)d, hits: %(hits)d, accuracy: %(accuracy).2f%%") % {"punches": result.punches, "hits": result.hits, "accuracy": result.hitPercentage})
		m.open()
		while(True):
			self.frameUpdate()
			r=m.frameUpdate()
			if r is not None:break
		# end while
	#end resultDialog
	def scorePostDialog(self,result):
		"""
		Shows the 'Do you want to post this score?' dialog. The result to post must be specified by the result parameter.

Returns False when the game is closed. Otherwise True.

		:param result: Result to post
		:type result: gameResult.GameResult
		"""
		m=window.menu()
		m.initialize(self,_("Score posting"),"",self.sounds["cursor.ogg"],self.sounds["confirm.ogg"],self.sounds["confirm.ogg"])
		m.append(_("Do you want to post this score to the scoreboard?"))
		m.append(_("Yes"))
		m.append(_("No"))
		while(True):
			m.open()
			while(True):
				self.frameUpdate()
				r=m.frameUpdate()
				if r is not None:break
			# end while the menu is active
			if r>0:break
		#end while, other than the top item is selected
		if r==1:#post
			adapter=scorePostingAdapter.AdapterBase()
			ret=adapter.post(result)
			if ret==scorePostingAdapter.RET_UNAVAILABLE:
				self.message(_("This build of Screaming Strike does not support score posting. Sorry!"))
				return True
			#end unavailable
			if ret==scorePostingAdapter.RET_CONNECTION_ERROR:
				self.message(_("There was an error while posting your score. Please try again later."))
				return True
			#end connection error
			self.message(_("Congratulations! Your score is ranked at %(pos)d! Keep up your great work!" % {"pos": ret}))
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
			self.wait(50)
		#end while
		self.music.pitch=100
	#end resetMusicPitch

	def message(self,msg):
		"""
		Shows a simple message dialog. This method is blocking; it won't return until user dismisses the dialog. While this method is blocking, onExit still works as expected.

		:param msg: Message to show.
		:type msg: str
		"""
		self.say(msg)
		while(True):
			self.frameUpdate()
			if True in (self.keyPressed(window.K_LEFT), self.keyPressed(window.K_RIGHT), self.keyPressed(window.K_UP), self.keyPressed(window.K_DOWN)): self.say(msg)#Message repeat
			if self.keyPressed(window.K_RETURN): break
		#end frame update
		bgtsound.playOneShot(self.sounds["confirm"])
	#end message

	def onExit(self):
		"""Extended onExit callback."""
		self.collectionStorage.save(COLLECTION_DATA_FILENAME)
		self.hsStorage.save(HIGHSCORE_DATA_FILENAME)
		return True
# end class ssAppMain

