# -*- coding: utf-8 -*-
# Screaming Strike player handler class
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
from bgtsound import *
import random
import bonusCounter
import enemy
import globalVars
import itemConstants
import itemEffects
import window

DEFAULT_PUNCH_RANGE = 4
DEFAULT_PUNCH_SPEED = 200

class Player():
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,field):
		self.field=field
		self.lives=3
		self.x=field.getCenterPosition()
		self.punchTimer=window.Timer()
		self.punchTimer=window.Timer()
		self.punching=False
		self.punchSpeed=DEFAULT_PUNCH_SPEED
		self.punchRange=DEFAULT_PUNCH_RANGE
		self.score=0
		self.punches=0
		self.hits=0
		self.hitPercentage=0
		self.consecutiveHitBonus=bonusCounter.BonusCounter()
		self.consecutiveHitBonus.initialize()
		self.consecutiveMissUnbonus=bonusCounter.BonusCounter()
		self.consecutiveMissUnbonus.initialize()
		self.consecutiveHits=0
		self.consecutiveMisses=0
		self.itemEffects=[]
		self.penetrate=False

	def frameUpdate(self):
		self.consecutiveHitBonus.frameUpdate()
		self.consecutiveMissUnbonus.frameUpdate()
		if self.punching is False and globalVars.appMain.wnd.keyPressed(window.K_SPACE): self.punchLaunch()
		if self.punching is True and self.punchTimer.elapsed>=self.punchSpeed: self.punchHit()
		if self.x!=0 and globalVars.appMain.wnd.keyPressed(window.K_LEFT): self.moveTo(self.x-1)
		if self.x!=self.field.getX()-1 and globalVars.appMain.wnd.keyPressed(window.K_RIGHT): self.moveTo(self.x+1)
		for elem in self.itemEffects[:]:
			if not elem.frameUpdate(): self.itemEffects.remove(elem)

	def punchLaunch(self):
		self.punches+=1
		self.punching=True
		s=sound()
		s.load(globalVars.appMain.sounds["fists.ogg"])
		s.pan=self.field.getPan(self.x)
		s.pitch=random.randint(90,110)
		s.play()
		self.punchTimer.restart()

	def punchHit(self):
		self.punching=False
		hit=0
		for pos in range(int(self.punchRange)+1):
			for elem in self.field.enemies:
				if elem.state==enemy.STATE_ALIVE and self.x==elem.x and elem.y==pos:
					elem.hit()
					hit+=1
					self.hits+=1
					self.consecutiveHits+=1
					self.processConsecutiveMisses()
					self.calcHitPercentage()#penetration would higher the percentage, but I don't care
					self.field.logDefeat()
					if not self.penetrate: break
				# end if
			# end for enemies
			if not self.penetrate and hit>0: break
			for elem in self.field.items:
				if elem.state==itemConstants.STATE_ALIVE and self.x==elem.x and elem.y==pos:
					elem.hit()
					self.processItemHit(elem)
					hit=True
					self.hits+=1
					self.consecutiveHits+=1
					self.processConsecutiveMisses()
					self.calcHitPercentage()
					if not self.penetrate: break
				# end if
			# end for items
		# end for range
		if not hit: self.punchMiss()
	# end punchHit

	def punchMiss(self):
		self.consecutiveMisses+=1
		if self.hits>0: self.calcHitPercentage()
		self.processConsecutiveHits()

	def processConsecutiveHits(self):
		if self.consecutiveHits>5:
			self.field.log(_("%(hits)d consecutive hits bonus!") % {"hits": self.consecutiveHits})
			self.addScore(self.consecutiveHits*self.consecutiveHits*self.field.level*self.field.level)
			self.consecutiveHitBonus.start(self.consecutiveHits)
		# end if
		self.consecutiveHits=0

	def processConsecutiveMisses(self):
		if self.consecutiveMisses>5:
			self.field.log(_("%(misses)d consecutive misses penalty!") % {"misses": self.consecutiveMisses})
			self.addScore(self.consecutiveMisses*self.consecutiveMisses*self.field.level*self.field.level*-1)
			self.consecutiveMissUnbonus.start(self.consecutiveMisses*-1)
		# end if
		self.consecutiveMisses=0

	def processItemHit(self,it):
		if it.type==itemConstants.TYPE_NASTY:
			self.processNastyItemHit(it)
		else:
			self.processGoodItemHit(it)

	def processNastyItemHit(self,it):
		if it.identifier==itemConstants.NASTY_SHRINK:
			e=itemEffects.ShrinkEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if it.identifier==itemConstants.NASTY_BLURRED:
			e=itemEffects.BlurredEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if it.identifier==itemConstants.NASTY_SLOWDOWN:
			e=itemEffects.SlowDownEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return

	def processGoodItemHit(self,it):
		if it.identifier==itemConstants.GOOD_MEGATONPUNCH:
			existing=self.findEffect("Megaton punch")
			if existing is None:
				e=itemEffects.MegatonPunchEffect()
				e.initialize(self)
				e.activate()
				self.itemEffects.append(e)
			else:
				existing.extend(itemConstants.BASE_EFFECT_TIME)
			return
		if it.identifier==itemConstants.GOOD_BOOST:
			e=itemEffects.BoostEffect()
			e.initialize(self)
			e.activate()
			self.itemEffects.append(e)
			return
		if it.identifier==itemConstants.GOOD_PENETRATION:
			existing=self.findEffect("Penetration")
			if existing is None:
				e=itemEffects.PenetrationEffect()
				e.initialize(self)
				e.activate()
				self.itemEffects.append(e)
			else:
				existing.extend(itemConstants.BASE_EFFECT_TIME)
			return
		if it.identifier==itemConstants.GOOD_DESTRUCTION:
			self.field.startDestruction()
			return
		if it.identifier==itemConstants.GOOD_EXTRALIFE:
			self.lives+=1
			self.field.log(_("Extra life! (now %(lives)d lives)") % {"lives": self.lives})
			s=sound()
			s.load(globalVars.appMain.sounds["extraLife.ogg"])
			s.pitch=60+(self.lives*10)
			s.play()
			return

	def findEffect(self,name):
		for elem in self.itemEffects:
			if elem.name==name: return elem
		return None

	def setPunchRange(self,r):
		previous=self.punchRange
		self.field.log(_("The effective range of your Punch is now %(range)d (from %(from)d)") % {"range": r, "from": previous})
		self.punchRange=r

	def setPunchSpeed(self,s):
		previous=self.punchSpeed
		self.field.log(_("The speed of your punch is now %(speed)d milliseconds (from %(from)d)") % {"speed": s, "from": previous})
		self.punchSpeed=s

	def setPenetration(self,p):
		if p is True:
			self.field.log(_("Your punches now penetrate enemies and items!"))
		else:
			self.field.log(_("Your punches no longer penetrate enemies and items!"))
		self.penetration=p

	def calcHitPercentage(self):
		self.hitPercentage=self.hits/self.punches*100
	def moveTo(self,p):
		self.x=p
		s=sound()
		s.load(globalVars.appMain.sounds["change.ogg"])
		s.pan=self.field.getPan(self.x)
		s.play()

	def hit(self):
		self.lives-=1
		self.field.log(_("You've been slapped! (%(lives)d HP remaining)") % {"lives": self.lives})
		s=sound()
		if self.lives>0:
			s.load(globalVars.appMain.sounds["attacked.ogg"])
			s.play()
		else:
			s.load(globalVars.appMain.sounds["gameover.ogg"])
			s.volume=-10
			s.play()

	def addScore(self,score):
		self.score+=score
		which=_("added")
		if score<=0: which=_("subtracted")
		self.field.log(_("Point: %(added).1f %(changestr)s (%(total).1f)") % {"added": score, "changestr": which, "total": self.score})
# end class Player
