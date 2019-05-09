# -*- coding: utf-8 -*-
#Basic window, timer, speech, menu handling
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

from copy import copy
import pygame
import accessible_output2.outputs.auto
from pygame.locals import *
from dialog import *
from bgtsound import *
class SingletonWindow():
	"""Just a pygame window wrapper. As the name implies, you mustn't create multiple singletonWindow's in your game. You should inherit this class and make your own app main class to make your code easy to read."""
	def __init__(self):
		pygame.init()
		self.clock=pygame.time.Clock()

	def __del__(self):
		pygame.quit()

	def initialize(self,x,y,ttl):
		"""
		Initializes the game window. Returns True on success or False for failure.

		:rtype: bool
		"""
		self.screen = pygame.display.set_mode((x, y))
		pygame.display.set_caption(ttl)
		self.keys=[0]*255
		self.previousKeys=[0]*255
		self.speech=accessible_output2.outputs.auto.Auto()
		return True

	def frameUpdate(self):
		"""
A function that must be called once per frame. Calling this function will keep the 60fps speed.

When user presses alt+f4 or the x icon, this function attempts to shut down the game by calling self.exit method. It is possible that the exit message is canceled by the onExit callback currently set.
"""
		self.clock.tick(60)
		self.screen.fill((255,63,10,))
		pygame.display.update()
		self.previousKeys=copy(self.keys)
		self.keys=pygame.key.get_pressed()
		if self.keys[K_LALT] and self.keys[K_F4]: self.exit()
		for event in pygame.event.get():
			if event.type == QUIT: self.exit()
		#end event
	#end frameUpdate

	def keyPressed(self,key):
		"""
		Retrieves if the specified key has changed to "pressed" from "not pressed" at the last frame. Doesn't cause key repeats.

		:rtype: bool
"""
		return self.keys[key] and not self.previousKeys[key]

	def keyPressing(self,key):
		"""
		Retrieves if the specified key is being pressed. Key repeats at 60rp/sec.

		:rtype: bool
"""
		return self.keys[key]

	def wait(self,msec):
		"""waits for a specified period of milliseconds while keeping the window looping. """
		t=Timer()
		while t.elapsed<msec:
			self.frameUpdate()
		#end loop
	#end wait

	def say(self,str):
		"""tts speech"""
		self.speech.speak(str)

	def exit(self):
		"""Attempt to exit the game. It is canceled if the onExit callback is set and it returned False."""
		if not self.onExit(): return
		sys.exit()

	def onExit(self):
		"""
		Override this method to define your own onExit code. It is automatically called from self.frameUpdate method when the game is being closed.

		You should return True when game can exit normally or False if you want to cancel the exit event.

		:rtype: bool
		"""
		return True#This is default

#end class singletonWindow

class Timer:
	"""A simple timer class like bgt."""
	def __init__(self):
		self.restart()

	def restart(self):
		"""Restarts this timer."""
		self.startTick=pygame.time.get_ticks()

	@property
	def elapsed(self):
		"""
		Returns the elapsed time in milliseconds.

		:rtype: int
		"""
		return pygame.time.get_ticks()-self.startTick
#end class Timer

class menu:
	"""A simple nonblocking menu class."""
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,wnd,ttl="no title", items="", cursorSound=None, enterSound=None, cancelSound=None):
		"""Initializes the menu with window instance, title and initial menu items. Requires a singletonWindow instance for this menu to work. Menu items should be a sequence of strings (not an array). the "#" character is used as the menu delimitor. """
		self.wnd=wnd
		self.title=ttl
		self.items=[]
		if items!="": self.items=items.split("#")
		self.cursor=0
		self.cursorSound=cursorSound
		self.enterSound=enterSound
		self.cancelSound=cancelSound

	def add(self,str):
		"""Adds one or multiple menu items. # is used as the delimitor. """
		lst=str.split("#")
		for elem in lst:
			self.items.append(elem)

	def open(self):
		"""Starts the menu. You should call frameUpdate() to keep the menu operate after this. """
		if len(self.items)==0: return
		self.wnd.say("%s, %s" % (self.title, self.items[self.cursor]))

	def frameUpdate(self):
		"""The frame updating function for this menu. You should call your window's frameUpdate prior to call this function. Returns None for no action, -1 for cancellation and 0-based index for being selected. """
		if self.wnd.keyPressed(K_UP) and self.cursor!=0: self.moveTo(self.cursor-1)
		if self.wnd.keyPressed(K_DOWN) and self.cursor!=len(self.items)-1: self.moveTo(self.cursor+1)
		if self.wnd.keyPressed(K_HOME) and self.cursor!=0: self.moveTo(0)
		if self.wnd.keyPressed(K_END) and self.cursor!=len(self.items): self.moveTo(len(self.items)-1)
		if self.wnd.keyPressed(K_SPACE): self.moveTo(self.cursor)
		if self.wnd.keyPressed(K_ESCAPE):
			self.cancel()
			return -1
		#end cancel
		if self.wnd.keyPressed(K_RETURN):
			self.enter()
			return self.cursor
		#end enter
		return None
	#end frameUpdate

	def cancel(self):
		"""Internal function which is triggered when canceling the menu. """
		if self.cancelSound is not None: playOneShot(self.cancelSound)

	def enter(self):
		"""Internal function which is triggered when selecting an option. """
		if self.enterSound is not None: playOneShot(self.enterSound)

	def getCursorPos(self):
		"""Returns the current cursor position. """
		return self.cursor

	def moveTo(self,c):
		"""Moves the menu cursor to the specified position and reads out the cursor. """
		if self.cursorSound is not None: playOneShot(self.cursorSound)
		self.cursor=c
		self.wnd.say(self.items[self.cursor])
#end class menu
