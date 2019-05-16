# -*- coding: utf-8 -*-
# Screaming Strike update checker / downloader client
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import platform
import threading
import urllib.request
import bgtsound
import globalVars

"""This module contains UpdateChecker class, which can be used as update checking client. It also contains updateDownloader."""

RET_USING_LATEST=1
RET_NEW_VERSION_AVAILABLE=2
RET_NOT_SUPPORTED=0
RET_CONNECTION_ERROR=-1
RET_NEVER_CHECKED=-2

class Checker(object):
	"""This object checks for updates"""
	def __init__(self):
		self.version=None#Version retrieved from server
		self.serverAddress=""#https://www.yourhost.com/screamingstrike/updateChecker.php
		self.localVersion=1.00#Default
		self.lastResult=RET_NEVER_CHECKED
		self.lastError=""
		self.working=False
		self.thread=None

	def initialize(self,version,address):
		"""Initializes this client with the given local version and server address. If working thread is active, this method does nothing.

		:param version: Current local version.
		:type version: float
		:param address: Server address. It should point to updateChecker.php.
		:type address: str
		"""
		if self.working: return
		self.serverAddress=address
		self.currentVersion=version

	def run(self):
		"""Runs the update check as a background thread. If it's already checking updates, this method does nothing. If the server URL is not set, it sets the last result to RET_NOT_SUPPORTED."""
		if self.working: return
		self.thread=threading.Thread(target=self._thread)
		self.thread.setDaemon(True)
		self.thread.start()

	def _thread(self):
		"""Internal thread method. You should not call this method."""
		self.working=True
		if self.serverAddress=="":
			self.lastResult=RET_NOT_SUPPORTED
			self.working=False
			return
		#end URL not suplied
		req=urllib.request.Request(self.serverAddress+"?updatecheck=true&platform="+platform.system())
		try:
			with urllib.request.urlopen(req) as res:
				body=res.read()
			#end with
		except urllib.error.URLError as r:
			self.lastResult=RET_CONNECTION_ERROR
			self.lastError=str(r)
			self.working=False
			return
		#end except
		body=body.decode()
		self.version=float(body)
		self.lastResult=RET_NEW_VERSION_AVAILABLE if self.version>self.currentVersion else RET_USING_LATEST
		self.lastError=""
		self.working=False
		return
	#end _thread

	def wait(self):
		"""Blocks until the update checking finishes."""
		if self.thread: self.thread.join()

	def getLastResult(self):
		"""Retrieves the result of last checked update. Returns RET_** values.

		:rtype: int
		"""
		return self.lastResult
	#end getLastResult

	def getLastError(self):
		"""Retrieves the last error string.

		:rtype: str
		"""
		return self.lastError

	def getVersion(self):
		"""Returns the version number retrieved from the server.

		:rtype: float
		"""
		return self.version

class Downloader(object):
	"""This object downloads the specified file as background thread."""
	def __init__(self):
		self.thread=None
		self.url=None
		self.localname=None
		self.completeCallback=None
		self.working=False
		self.succeeded=False
		self.lastError=None

	def initialize(self,url,localname,completeCallback):
		"""Initializes the downloader.

		:param url: URL.
		:type url: str
		:param localname: Local file name.
		:type localname: str
		:param completeCallback: Callback when download finished.
		:type completeCallback: callable
		"""
		if self.working: return
		self.url=url
		self.localname=localname
		self.completeCallback=completeCallback
		self.percentage=0
		self.totalSize=0
		self.receivedSize=0

	def run(self):
		"""Starts the update"""
		if not self.url: return
		if not self.localname: return
		self.thread=threading.Thread(target=self._thread)
		self.thread.setDaemon(True)
		self.thread.start()

	def _progress(self, blockCount,blockSize,totalSize):
		"""Internal progress callback. You should not call this method."""
		self.receivedSize=blockCount*blockSize
		self.totalSize=totalSize#Overwriting unnecessarily, but don't care
		self.percentage=100.0*self.receivedSize/self.totalSize

	def _thread(self):
		"""Internal thread. You should not call this method."""
		self.working=True
		try:
			urllib.request.urlretrieve(url=self.url, filename=self.localname, reporthook=self._progress)
		except urllib.error.URLError as r:
			self.succeeded=False
			self.working=False
			self.lastError=str(r)
			if self.completeCallback: self.completeCallback()
			return
		#end except
		self.succeeded=True
		if self.completeCallback: self.completeCallback()
		self.working=False

	def hasSucceeded(self):
		"""Retrieves if the download has succeeded.

		:rtype: bool
		"""
		return self.succeeded

	def getPercentage(self):
		"""Gets the percentage of download.

		:rtype: float
		"""
		return self.percentage

	def getReceivedSize(self):
		"""Gets the total received size so far.

		:rtype: int
		"""
		return self.receivedSize

	def getTotalSize(self):
		"""Gets the total size of download.

		:rtype: int
		"""
		return self.totalSize

	def isWorking(self):
		"""Retrieves if the download is in progress.

		:rtype: bool
		"""
		return self.working

	def getLocalName(self):
		"""Retrieves the local file name.

		:rtype: str
		"""
		return self.localname

	def getLastError(self):
		"""Retrieves the last error.

		:rtype: str
		"""
		return self.lastError
