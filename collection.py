# -*- coding: utf-8 -*-
# Screaming Strike collection handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
"""This module contains collectionStorage and collectionCounter. CollectionStorage is used as it implies, and CollectionCounter is created for every game session and that object accesses the storage."""
import bgtsound
import globalVars
import window

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
			f=open(file,"w")
		except IOError:
			return False
		#end except
		f.write(tmp)
		f.close()
		return True

	def inclement(self,number):
		"""
		Inclements the specified scream count by one. Returns True if it is unlocked, otherwise False.

		:param number: Scream number.
		:type number: int
:rtype: bool
		"""
		if number>self.screamNum: return
		self.screams[number]+=1
		return self.screams[number]==UNLOCK_TRIGGER

	def isUnlocked(number):
		"""Retrieves if the specified scream is unlocked.

		:rtype: bool
		"""
		return self.screams[number] >=UNLOCK_TRIGGER
#end class CollectionHandler

class CollectionCounter(object):
	"""This object counts screams played in a game session. Call frameUpdate for frame updating, and inclement when someone screamed. It also stores a full log of who has been unlocked in this session. You can call getLog and show the preview of what has been unlocked after the session ends."""
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

	def inclement(self,number):
		"""Inclements the specified scream number. If it is unlocked by this call, unlock event is also triggered.

		:param number: Scream number.
		:type number: int
"""
		if self.storage is None: return
		if self.storage.inclement(number) is True: self.unlock(number)

	def unlock(self):
		"""Triggers one unlock sound. You can call this method multiple times really quickly; this object delays the following playbacks not to make them overlap."""
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

