# -*- coding: utf-8 -*-
# Screaming Strike collection handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
"""This module contains collectionStorage, collectionCounter and collectionDialog. CollectionStorage is used as it implies, and CollectionCounter is created for every game session and that object accesses the storage. """
import zlib

import bgtsound
import globalVars
import window
import enemy

UNLOCK_TRIGGER=10
UNLOCKED_SOUND_FILENAME="unlock.ogg"
UNLOCKED_SOUND_PLAYBACK_INTERVAL=300

class CollectionStorage(object):
	"""
	This object stores each number of screams played.
	"""
	def __init__(self):
		self.screamNum=0
		self.screams=[]

	def initialize(self,screamNum,file=""):
		"""
		Initializes the counter. Recalling this function will irase previous settings and overwrite with the new one.

		:param screamNum: Number of screams. This value is used when filename is not given or it is invalid.
		:type screamNum: int
		:param file: The file from which counts are loaded. If this method succeeds in loading this file and screanNum is grater than the number of records in the file, the rest is automatically populated by zeros.
		:type file: str
		"""
		self.screams=[]
		if file=="":
			self.reserve(screamNum)
			return
		#end not given a file
		try:
			f=open(file,"rb")
		except IOError:
			self.reserve(screamNum)
			return
		#end except
		nums=zlib.decompress(f.read()).decode().split(",")
		for elem in nums:
			self.screams.append(int(elem))
		#end for
		if len(nums)<screamNum: self.reserve(screamNum-len(nums))
		self.screamNum=screamNum
	#end initialize

	def reserve(self,num):
		"""
		Populates the counts list with the specified number of zeros. Called from initialize. This methods appends zeros and does not affect existing elements in the list.

		:param num: count
		:type num: int
		"""
		for i in range(num):
			self.screams.append(0)
		#end for
	#end reserve

	def reset(self):
		"""Resets all the elements to 0."""
		for i in range(len(self.screams)):
			self.screams[i]=0
		#end for
	#end reset

	def save(self,file):
		"""Saves the current status to a file. The destination file is overwritten. If IO error occurs, this method returns False, otherwise True.

		:param File: filename to save.
		:type file: str
		:rtype: bool
		"""
		tmp=""
		for elem in self.screams:
			tmp+=str(elem)+","
		#end for
		tmp=tmp.rstrip(",")
		try:
			f=open(file,"wb")
		except IOError:
			return False
		#end except
		f.write(zlib.compress(tmp.encode()))
		f.close()
		return True

	def increment(self,number):
		"""
		Increments the specified scream count by one. Returns True if it is unlocked, otherwise False.

		:param number: Scream number.
		:type number: int
:rtype: bool
		"""
		if number>self.screamNum: return
		self.screams[number]+=1
		return self.screams[number]==UNLOCK_TRIGGER

	def get(self,number):
		"""Retrieves the number of plays of the specified scream.

		:rtype: int
		"""
		return self.screams[number]

	def isUnlocked(self,number):
		"""Retrieves if the specified scream is unlocked.

		:rtype: bool
		"""
		return self.screams[number] >=UNLOCK_TRIGGER
#end class CollectionHandler

class CollectionCounter(object):
	"""This object counts screams played in a game session. Call frameUpdate for frame updating, and increment when someone screamed. It also stores a full log of who has been unlocked in this session. You can call getLog and show the preview of what has been unlocked after the session ends."""
	def __init__(self):
		self.stack=0#number of stacks
		self.timer=window.Timer()
		self.storage=None
		self.log=[]
	#end __init__

	def initialize(self,storage):
		"""Initializes this counter.

		:param storage: Storage to which this counter is connected.
		:type storage: CollectionStorage
		"""
		self.storage=storage

	def increment(self,number):
		"""increments the specified scream number. If it is unlocked by this call, unlock event is also triggered.

		:param number: Scream number.
		:type number: int
		"""
		if self.storage is None: return
		if self.storage.increment(number) is True: self.unlock(number)

	def unlock(self,number):
		"""Triggers one unlock sound. You can call this method multiple times really quickly; this object delays the following playbacks not to make them overlap.

		:param number: Scream number to unlock.
		:type number: int
		"""
		self.stack+=1
		self.log.append(number)
	#end trigger

	def frameUpdate(self):
		"""If the time is right, pops a stack and plays an unlock sound."""
		if self.stack==0: return
		if self.timer.elapsed>=UNLOCKED_SOUND_PLAYBACK_INTERVAL:
			self.stack-=1
			bgtsound.playOneShot(globalVars.appMain.sounds[UNLOCKED_SOUND_FILENAME])
			self.timer.restart()
		#end if timer
	#end frameUpdate

	def getLog(self):
		"""Retrieves the log of unlocked screams in a list of integers representing scream numbers.

		:rtype: list
		"""
		return self.log
	#end getLog
#end class CollectionCounter

class CollectionDialog(object):
	"""Instantiate this object and call the run method to open the collection dialog."""
	def run(self,appMain):
		"""Runs the collection dialog.

		:param wnd: Window on which this dialog runs.
		:type appMain: ssAppMain.SsAppMain
		"""
		self.appMain=appMain
		self.sound=None
		appMain.say(_("Use your left and right arrows to brows your collections, then press enter to make your unlocked one scream. You can move through your unlocked items with shift + left or right. To play with pitch changing, hold down up and down arrows. Press escape when you're satisfied."))
		self.index=0
		self.pitch=100
		self.pitchTimer=window.Timer()
		self.lastHold=0
		self.holdTimer=window.Timer()

		while(True):
			appMain.frameUpdate()
			if appMain.keyPressed(window.K_ESCAPE): break
			if appMain.keyPressing(window.K_LSHIFT) or appMain.keyPressing(window.K_RSHIFT):
				if appMain.keyPressed(window.K_LEFT): self.searchUnlocked(-1)
				if appMain.keyPressed(window.K_RIGHT): self.searchUnlocked(1)
			else:
				left=appMain.keyPressing(window.K_LEFT)
				right=appMain.keyPressing(window.K_RIGHT)
				if not left and not right: self.lastHold=0
				if left and self.index!=0: self.moveTo(self.index-1)
				if right and self.index!=self.appMain.numScreams-1: self.moveTo(self.index+1)
			#end shift or not
			if appMain.keyPressed(window.K_SPACE): self.moveTo(self.index)
			if appMain.keyPressed(window.K_RETURN) and appMain.collectionStorage.isUnlocked(self.index): self.play(self.index)
			if appMain.keyPressing(window.K_UP) and self.pitchTimer.elapsed>=50 and self.pitch!=enemy.SCREAM_PITCH_HIGH: self.changePitch(self.pitch+1)
			if appMain.keyPressing(window.K_DOWN) and self.pitchTimer.elapsed>=50 and self.pitch!=enemy.SCREAM_PITCH_LOW: self.changePitch(self.pitch-1)
		#end while
		bgtsound.playOneShot(appMain.sounds["confirm.ogg"])
	#end run

	def moveTo(self,index):
		"""Updates the cursor position.

		:param index: New position.
		:type index: int
		"""
		#key hold. Should have reused the menu class one, but I'm lazy.
		if self.lastHold==1 and self.holdTimer.elapsed<600: return
		if self.lastHold==2 and self.holdTimer.elapsed<50: return
		self.holdTimer.restart()
		if self.lastHold<2: self.lastHold+=1
		self.index=index
		unlocked=self.appMain.collectionStorage.isUnlocked(index)
		if unlocked:
			bgtsound.playOneShot(self.appMain.sounds["cursor.ogg"])
			s=_("Unlocked")
		else:
			bgtsound.playOneShot(self.appMain.sounds["cursor.ogg"], pitch=80)
			s=_("Locked")
		#end if locked or not
		self.appMain.say(_("No.%(no)d, %(status)s, %(plays)d") % {"no": index, "status": s, "plays": self.appMain.collectionStorage.get(index)})
	#end moveTo

	def searchUnlocked(self,direction):
		"""Searches for the next / previous unlocked scream. 1=right, -1=left. Otherwise, ignored.

		:param direction: Direction.
		"""
		if direction!=-1 and direction!=1: return
		found=False
		i=self.index
		while True:
			i+=direction
			if i==-1 or i==self.appMain.numScreams: break
			if self.appMain.collectionStorage.isUnlocked(i):
				found=i
				break
			#end found?
		#end while
		if found: self.moveTo(i)
	#end searchUnlocked

	def play(self,index):
		"""Plays a scream.

		:param pos: Scream number.
		"""
		if self.sound: self.sound.stop()
		self.sound=bgtsound.sound()
		self.sound.load(self.appMain.sounds["scream%d.ogg" % index])
		self.sound.pitch=self.pitch
		self.sound.play()
		bgtsound.playOneShot(self.appMain.sounds["confirm.ogg"])
	#end play

	def changePitch(self,pitch):
		"""Changes the playback pitch.

		:param pitch: New pitch.
		"""
		self.pitch=pitch
		if self.sound: self.sound.pitch=self.pitch
	#end changePitch
