# -*- coding: utf-8 -*-
#Basic window, timer, speech, menu handling
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)

from copy import copy
import pygame
import wx
import sys
import accessible_output2.outputs.auto
from pygame.locals import *
from dialog import *
from bgtsound import *
class SingletonWindow():
	"""Just a pygame window wrapper. As the name implies, you mustn't create multiple singletonWindow's in your game. You should inherit this class and make your own app main class to make your code easy to read."""
	def __init__(self):
		self.wxInstance=wx.App()
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
		print("exiting")
		if not self.onExit(): return
		sys.exit()

	def onExit(self):
		"""
		Override this method to define your own onExit code. It is automatically called from self.frameUpdate method when the game is being closed.

		You should return True when game can exit normally or False if you want to cancel the exit event.

		:rtype: bool
		"""
		return True#This is default

	def input(self,title,message):
		"""Shows a text input dialog and returns what was input by the user. Returns None when canceled."""
		ret=None
		dlg=wx.TextEntryDialog(None, message,title)
		if dlg.ShowModal()==wx.ID_OK: ret=dlg.GetValue()
		dlg.Destroy()
		return ret
	#end input
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

STR_TO_KEY={
	"A": K_a,
	"B": K_b,
	"C": K_c,
	"D": K_d,
	"E": K_e,
	"F": K_f,
	"G": K_g,
	"H": K_h,
	"I": K_i,
	"J": K_j,
	"K": K_k,
	"L": K_l,
	"M": K_m,
	"N": K_n,
	"O": K_o,
	"P": K_p,
	"Q": K_q,
	"R": K_r,
	"S": K_s,
	"T": K_t,
	"U": K_u,
	"V": K_v,
	"W": K_w,
	"X": K_x,
	"Y": K_y,
	"Z": K_z,
	"0": K_0,
	"1": K_1,
	"2": K_2,
	"3": K_3,
	"4": K_4,
	"5": K_5,
	"6": K_6,
	"7": K_7,
	"8": K_8,
	"9": K_9
}

class menu:
	"""A simple nonblocking menu class."""
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,wnd,ttl="no title", items=None, cursorSound=None, enterSound=None, cancelSound=None):
		"""
		Initializes the menu with window instance, title and initial menu items. Requires a singletonWindow instance for this menu to work. Menu items should be a sequence of strings (not an array). the "#" character is used as the menu delimitor. 

		:param wnd: Window to which this menu is bound.
		:type wnd: SingletonWindow
		:param ttl: Menu title.
		:type ttl: str
		:param items: Default items.
		:type items: list
		:param CursorSound: Sample instance played when user cycles through the menu items.
		:type enterSound: sound_lib.sample
		:param enterSound: Sample instance played when user presses enter on a menu item.
		:type enterSound: sound_lib.sample
		:param cancelSound: Sample instance played when user cancels the menu.
		:type enterSound: sound_lib.sample
		"""
		self.wnd=wnd
		self.title=ttl
		self.items=[]
		self.shortcuts=[]
		if items: self.append(items)
		self.cursor=0
		self.cursorSound=cursorSound
		self.enterSound=enterSound
		self.cancelSound=cancelSound

	def append(self,lst):
		"""Adds one or multiple menu items. """
		if isinstance(lst,str):
			self.append_internal(lst)
			return
		#end single append
		for elem in lst:
			self.append_internal(elem)

	def append_internal(self,elem):
		"""Parses and adds a single item. Called from append.

		:param elem: Element to add.
		"""
		shortcut, shortcut_str=self.parseShortcut(elem)
		if shortcut:
			elem=elem[0:len(elem)-2]
			self.shortcuts.append((shortcut,len(self.items)))
		#end if shortcut registration
		self.items.append((elem,shortcut_str,shortcut))

	def parseShortcut(self,elem):
		"""Parses the menu item string and returns shortcut keycode and string if detected. Otherwise, set both as None.
		:param elem: Element to parse.
		"""
		shortcut=None
		shortcut_str=None
		l=len(elem)
		if l<=3: return None, None
		last=elem[l-2:l].upper()
		if last[0]=="&":
			try:
				cmd=STR_TO_KEY[last[1]]
			except KeyError:
				pass
			else:
				shortcut=cmd
				shortcut_str=last[1]
			#end else
		#end if shortcut input exists
		return shortcut, shortcut_str

	def open(self):
		"""Starts the menu. You should call frameUpdate() to keep the menu operate after this. """
		if len(self.items)==0: return
		self.wnd.say("%s, %s" % (self.title, self.getReadStr()))

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
		if len(self.shortcuts)>0:
			for command in STR_TO_KEY.values():
				if self.wnd.keyPressed(command): return self.processShortcut(command)
			#end shortcut
		#end at least one shortcut is active
		return None
	#end frameUpdate

	def processShortcut(self,code):
		"""Search for the shortcut actions that is associated with the given command. Returns the index if one item is matched and instantly selected, otherwise None. This method may move focus or trigger the enter event as the result of searching.

		:param code: key code.
		:type code: int
		"""
		matched=[]
		for elem in self.shortcuts:
			if elem[0]==code: matched.append(elem)
		#end for
		if len(matched)==0: return
		if len(matched)==1:
			self.cursor=matched[0][1]
			self.enter()
			return self.cursor
		#end instant selection
		i=self.cursor
		found=False
		while i<len(self.items)-1:
			i+=1
			if self.items[i][2]==code:
				found=True
				break
			#end if
		#end while
		if found:
			self.moveTo(i)
			return None
		#end if found at the lower column
		#Research from the top
		i=-1
		while i<len(self.items)-1:
			i+=1
			if self.items[i][2]==code:
				found=True
				break
		if found:
			self.moveTo(i)
			return None
		#end research
	#end processShortcut

	def cancel(self):
		"""Internal function which is triggered when canceling the menu. """
		if self.cancelSound is not None: playOneShot(self.cancelSound)

	def enter(self):
		"""Internal function which is triggered when selecting an option. """
		if self.enterSound is not None: playOneShot(self.enterSound)

	def getCursorPos(self):
		"""Returns the current cursor position. """
		return self.cursor

	def getString(self,index):
		"""Retrieves the menu item string at the specified index. Returns empty string when out of bounds.

		:param index: Index.
		:rtype: str
		"""
		if index<0 or index>=len(self.items): return ""
		return self.items[index][0]

	def moveTo(self,c):
		"""Moves the menu cursor to the specified position and reads out the cursor. """
		if self.cursorSound is not None: playOneShot(self.cursorSound)
		self.cursor=c
		self.wnd.say(self.getReadStr())
	#end moveTo

	def getReadStr(self):
		"""Returns a string which should be used as readout string for the current cursor.

:rtype: str
"""
		s=self.items[self.cursor][0]
		if self.items[self.cursor][1] is not None: s+=", "+self.items[self.cursor][1]
		return s

	def isLast(self,index):
		"""Retrieves if the given index is the last item of the menu. This is particularly useful when you want to bind the last action to exit or close.

		:param index: index.
		:type index: int
		:rtype: bool
		"""
		return self.cursor==len(self.items)-1

#end class menu
