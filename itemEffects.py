# -*- coding: utf-8 -*-
# Screaming Strike item effects
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import bgtsound
import random

import globalVars
import itemConstants
import window

class ItemEffectBase(object):
	def __init__(self):
		pass
	def __del__(self):
		pass
	def initialize(self,player,onSound,offSound,name):
		self.player=player
		self.active=False
		self.timer=window.Timer()
		self.onSound=onSound
		self.offSound=offSound
		self.lasts=itemConstants.BASE_EFFECT_TIME
		self.name=name

	def activate(self):
		s=bgtsound.sound()
		s.load(self.onSound)
		s.play()
		self.active=True
		self.timer.restart()
		self.player.field.log(_("A new \"%(item)s\" effect is starting!") % {"item": self.name})

	def deactivate(self):
		s=bgtsound.sound()
		s.load(self.offSound)
		s.play()
		self.active=False
		self.player.field.log(_("One of your \"%(item)s\" effects is ending!") % {"item": self.name})

	def extend(self,ms):
		s=bgtsound.sound()
		s.load(self.onSound)
		s.pitch=130
		s.play()
		self.lasts+=ms
		self.player.field.log(_("Your \"%(item)s\" effect has been extended for %(extended)d milliseconds! (now %(newtime)d)") %  {"item": self.name, "extended": ms, "newtime": self.lasts-self.timer.elapsed})

	def frameUpdate(self):
		if self.active is not True: return False
		if self.timer.elapsed>=self.lasts:
			self.deactivate()
			return False
		return True

class ShrinkEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["shrink.ogg"],globalVars.appMain.sounds["shrinkFade.ogg"],"Shrink")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange*2)

class BlurredEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["blurred.ogg"],globalVars.appMain.sounds["blurredFade.ogg"],"Blurred")

	def frameUpdate(self):
		if super().frameUpdate() is False: return False
		if random.randint(1,10)==1:
			while(True):
				d=random.randint(0,self.player.field.getX()-1)
				if d!=self.player.x: break
			# end while
			self.player.moveTo(d)
		# whether to trigger blurring?
		return True
	# end frameUpdate

class SlowDownEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["slowDown.ogg"],globalVars.appMain.sounds["slowDownFade.ogg"],"Slow down")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

class MegatonPunchEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["megatonPunch.ogg"],globalVars.appMain.sounds["megatonPunchFade.ogg"],"Megaton punch")

	def activate(self):
		super().activate()
		self.player.setPunchRange(self.player.punchRange*5)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchRange(self.player.punchRange/5)

class BoostEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["boost.ogg"],globalVars.appMain.sounds["boostFade.ogg"],"Boost")

	def activate(self):
		super().activate()
		self.player.setPunchSpeed(self.player.punchSpeed/2)

	def deactivate(self):
		super().deactivate()
		self.player.setPunchSpeed(self.player.punchSpeed*2)

class PenetrationEffect(ItemEffectBase):
	def initialize(self,player):
		super().initialize(player,globalVars.appMain.sounds["penetration.ogg"],globalVars.appMain.sounds["penetrationFade.ogg"],"Penetration")

	def activate(self):
		super().activate()
		self.player.setPenetration(True)

	def deactivate(self):
		super().deactivate()
		self.player.setPenetration(False)
