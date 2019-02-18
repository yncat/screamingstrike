# -*- coding: utf-8 -*-
#Basic window and timer handling
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

from copy import copy
import pygame
from pygame.locals import *
from dialog import *
class singletonWindow():
	"""Just a pygame window wrapper. As the name implies, you mustn't create multiple singletonWindow's in your game. """
	def __init__(self):
		pass#I want to avoid doing initialization at constructor as much as possible, just my liking
	def __del__(self):
		pygame.quit()

	def initialize(self,x,y,ttl):
		"""Initializes the game window. Returns True on success or False for failure. """
		pygame.init()
		self.clock=pygame.time.Clock()
		self.screen = pygame.display.set_mode((x, y))
		pygame.display.set_caption(ttl)
		self.keys=[0]*255
		self.previousKeys=[0]*255
		return True

	def frameUpdate(self):
		"""A function that must be called once per frame. Calling this function will keep the 60fps speed. Returns True while the game is running and returns False when the process should exit. When returning false, you can immediately exit the game without caring about pygame termination because it's done automatically at the destructor. """
		self.clock.tick(60)
		self.screen.fill((255,63,10,))
		pygame.display.update()
		self.previousKeys=copy(self.keys)
		self.keys=pygame.key.get_pressed()
		if self.keys[K_LALT] and self.keys[K_F4]: return False
		for event in pygame.event.get():
			if event.type == QUIT: return False
		#end event
	#end frameUpdate

	def keyPressed(self,key):
		"""Retrieves if the specified key has changed to "pressed" from "not pressed" at the last frame. Doesn't cause key repeats.  """
		return self.keys[key] and not self.previousKeys[key]

	def keyPressing(self,key):
		"""Retrieves if the specified key is being pressed. Key repeats at 60rp/sec. """
		return self.keys[key]

	def wait(self,msec):
		"""waits for a specified period of milliseconds while keeping the window looping. Same as frameUpdate(), you should exit your game when this function returned false. """
		t=timer()
		while t.elapsed<msec:
			if self.frameUpdate() is False: return False
		#end loop
		return True
	#end wait
#end class singletonWindow

class timer:
	def __init__(self):
		self.restart()

	def restart(self):
		self.startTick=pygame.time.get_ticks()

	@property
	def elapsed(self):
		return pygame.time.get_ticks()-self.startTick

#end class timer