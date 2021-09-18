# -*- coding: utf-8 -*-
# Screaming Strike item effects
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import math
import bgtsound
import random

import globalVars
import itemConstants
import window


class ItemEffectBase(object):
    def initialize(self, player, onSound, offSound, name):
        self.paused = False
        self.player = player
        self.active = False
        self.timer = window.Timer()
        self.onSound = onSound
        self.offSound = offSound
        self.lasts = itemConstants.BASE_EFFECT_TIME
        self.name = name
        self.on = None
        self.off = None
        self.ex = None

    def activate(self, mode):
        self.on = bgtsound.sound()
        self.on.load(self.onSound)
        self.on.play()
        self.active = True
        self.timer.restart()
        self.player.field.log(_("A new \"%(item)s\" effect is starting!") % {"item": self.name})

    def deactivate(self, mode):
        self.off = bgtsound.sound()
        self.off.load(self.offSound)
        self.off.play()
        self.active = False
        self.player.field.log(_("One of your \"%(item)s\" effects is ending!") % {"item": self.name})

    def extend(self, ms):
        self.ex = bgtsound.sound()
        self.ex.load(self.onSound)
        self.ex.pitch = 130
        self.ex.play()
        self.lasts += ms
        self.player.field.log(_("Your \"%(item)s\" effect has been extended for %(extended)d milliseconds! (now %(newtime)d)") %
                              {"item": self.name, "extended": ms, "newtime": self.lasts - self.timer.elapsed})

    def summarize(self):
        """Returns the summary of this effect.

        :rtype: str
        """
        return _("%(name)s: %(sec).2f seconds left") % {"name": self.name, "sec": self.calculateTimeRemaining()}

    def calculateTimeRemaining(self):
        """
                Calculates the time after which this item expires in seconds.

                :rtype: float
        """
        return (self.lasts - self.timer.elapsed) / 1000

    def frameUpdate(self, mode):
        if self.active is not True:
            return False
        if self.timer.elapsed >= self.lasts:
            self.deactivate(mode)
            return False
        return True

    def setPaused(self, p):
        """Pauses / unpauses this effect."""
        if p == self.paused:
            return
        self.paused = p
        self.timer.setPaused(p)
        if self.on:
            self.on.setPaused(p)
        if self.off:
            self.off.setPaused(p)
        if self.ex:
            self.ex.setPaused(p)
    # end setPaused


class ShrinkEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["shrink.ogg"], globalVars.appMain.sounds["shrinkFade.ogg"], "Shrink")

    def activate(self, mode):
        super().activate(mode)
        self.player.setPunchRange(math.floor(self.player.punchRange * mode.getShrinkMultiplier()))

    def deactivate(self, mode):
        super().deactivate(mode)
        self.player.setPunchRange(math.ceil(self.player.punchRange / mode.getShrinkMultiplier()))


class BlurredEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["blurred.ogg"], globalVars.appMain.sounds["blurredFade.ogg"], "Blurred")

    def frameUpdate(self, mode):
        if super().frameUpdate(mode) is False:
            return False
        if random.randint(1, 10) == 1:
            while(True):
                d = random.randint(0, self.player.field.getX() - 1)
                if d != self.player.x:
                    break
            # end while
            self.player.moveTo(d)
        # whether to trigger blurring?
        return True
    # end frameUpdate


class SlowDownEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["slowDown.ogg"], globalVars.appMain.sounds["slowDownFade.ogg"], "Slow down")

    def activate(self, mode):
        super().activate(mode)
        self.player.setPunchSpeed(self.player.punchSpeed * mode.getSlowDownMultiplier())

    def deactivate(self, mode):
        super().deactivate(mode)
        self.player.setPunchSpeed(self.player.punchSpeed / mode.getSlowDownMultiplier())


class MegatonPunchEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["megatonPunch.ogg"], globalVars.appMain.sounds["megatonPunchFade.ogg"], "Megaton punch")

    def activate(self, mode):
        super().activate(mode)
        self.player.setPunchRange(self.player.punchRange * 5)

    def deactivate(self, mode):
        super().deactivate(mode)
        self.player.setPunchRange(self.player.punchRange / 5)


class BoostEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["boost.ogg"], globalVars.appMain.sounds["boostFade.ogg"], "Boost")

    def activate(self, mode):
        super().activate(mode)
        self.player.setPunchSpeed(self.player.punchSpeed / 2)

    def deactivate(self, mode):
        super().deactivate(mode)
        self.player.setPunchSpeed(self.player.punchSpeed * 2)


class PenetrationEffect(ItemEffectBase):
    def initialize(self, player):
        super().initialize(player, globalVars.appMain.sounds["penetration.ogg"], globalVars.appMain.sounds["penetrationFade.ogg"], "Penetration")

    def activate(self, mode):
        super().activate(mode)
        self.player.setPenetration(True)

    def deactivate(self, mode):
        super().deactivate(mode)
        self.player.setPenetration(False)
