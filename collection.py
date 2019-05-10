# -*- coding: utf-8 -*-
# Screaming Strike collection handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains CollectionHandler and UnlockSoundPlayer classes. CollectionHandler is what we use and UnlockSoundPlayer is an internal object used by CollectionHandler."""
import bgtsound
import window

UNLOCK_TRIGGER=10
UNLOCKED_SOUND_FILENAME="data/sounds/unlock.ogg"
UNLOCKED_SOUND_PLAYBACK_INTERVAL=300

class CollectionHandler(object):
	"""
	This object is used for counting number of plays of each scream. If It gets a certain number, the scream is unlocked. This class also logs unlocked screams in this session (since the last reset), so you can show the review of unlocked screams at the end of the game.
	"""
	def __init__(self):
		self.screamNum=0
		self.screams=[]
		self.unlockedLog=[]
		self.unlockSoundPlayer=UnlockSoundPlayer()

	def initialize(self,screamNum,file=""):
		"""
		Initializes the counter. Recalling this function will irase previous settings and overwrite with the new one.

		:param screamNum: Number of screams. This value is used when filename is not given or it is invalid.
		:type screamNum: int
		:param file: The file from which counts are loaded. If this method succeeds in loading this file, screamNum is ignored.
		:type file: str
		"""
		self.screams=[]
		try:
			f=open(file,"r")
		except IOError:
			self.reserve(screamNum)
			return
		#end except
		nums=f.read().split(",")
		for elem in nums:
			self.screams.append(int(elem))
		#end for
		self.screamNum=len(nums)
	#end initialize

	def reserve(self,num):
		"""
		Populates the counts list with the specified number of zeros. Called from initialize.

		:param num: count
		:type num: int
		"""
		self.screams=[0]*num
	#end reserve

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
		tmp.rstrip(",")
		try:
			f=open(filename,"w")
		except IOError:
			return False
		#end except
		f.write(tmp)
		f.close()
		return True

	def frameUpdate(self):
		"""Call this method once per frame to keep the unlock sound updated."""
		self.unlockSoundPlayer.frameUpdate()
		self.screamNum=num
	#end frameUpdate

	def inclement(self,number):
		"""
		Inclements the specified scream count by one. If it exceeds the unlock trigger, it also processes the unlock event. If the scream number is out of range, this method does nothing.

		:param number: Scream number.
		:type number: int
		"""
		if number>self.screamNum: return
		self.screams[number]+=1
		if self.screams[number]==UNLOCK_TRIGGER: self.unlock(number)
	#end inclement

	def unlock(self,number):
		"""
		Fires the unlock event to the specified scream number.

		:param number: Scream Number.
		:type number: int
		"""
		self.unlockedLog.append(number)
		self.unlockSoundPlayer.trigger()
	#end unlock

	def resetUnlockedLog(self):
		"""Resets the unlocked screams log."""
		self.unlockedLog=[]
	#end resetUnlockedLog

	def getUnlockedLog(self):
		"""Returns the list which contains unlocked scream numbers since the last reset.

		:rtype: list
		"""
		return self.unlockedLog
	#end getUnlockedLog
#end class CollectionHandler

class UnlockSoundPlayer(object):
	"""An object used to play scream unlocked sound. When multiple screams are unlocked at the same time, this object detects it and delay the playback automatically so that players can hear each sound properly."""
	def __init__(self):
		self.stack=0#number of stacks
		self.timer=window.Timer()
	#end __init__

	def trigger(self):
		"""Triggers one unlock sound. You can call this method multiple times really quickly; this object delays the following playbacks not to make them overlap."""
		self.stack+=1
	#end trigger

	def frameUpdate(self):
		"""If the time is right, pops a stack and plays an unlock sound."""
		if stack==0: return
		if self.timer.elapsed>=UNLOCKED_SOUND_PLAYBACK_INTERVAL:
			self.stack-=1
			bgtsound.playOneShot(UNLOCKED_SOUND_FILENAME)
			self.timer.restart()
		#end if timer
	#end frameUpdate

