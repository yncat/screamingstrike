# -*- coding: utf-8 -*-
# Screaming Strike bonus counter handler
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

from bgtsound import *
import globalVars
import window

class BonusCounter():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self):
		self.active=False
		self.countTimer=window.Timer()
		self.number=0
		self.current=0
	def start(self,number):
		if number==0: return
		self.number=number
		self.current=0
		self.countTimer.restart()
		self.active=True
		self.count()
	def frameUpdate(self):
		if self.active is True and self.countTimer.elapsed>=self.nextCountTime: self.count()
	def count(self):
		s=sound()

		if self.number>0:
			self.current+=1
			s.load(globalVars.appMain.sounds["bonus.ogg"])
			p=75+(self.current*5)
			if p>300: p=300
		else:
			self.current-=1
			s.load(globalVars.appMain.sounds["unbonus.ogg"])
			p=150+(self.current*3)
			if p<50: p=50
		# end if
		s.pitch=p
		s.play()
		if self.current==self.number:
			self.active=False
			return
		w=200-(abs(self.current)*10)
		if w<50: w=50
		self.nextCountTime=w
		self.countTimer.restart()
