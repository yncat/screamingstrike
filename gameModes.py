# -*- coding: utf-8 -*-
# Screaming Strike game mode handlers
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import math
import random
import bonusCounter
import item
import itemConstants
import window

NORMAL = 0
ARCADE = 1
CLASSIC = 2
BURDEN = 3
ALL_MODES_STR = ["Normal", "Arcade", "Classic", "Burden"]


class ModeHandlerBase(object):
    def __init__(self):
        self.allowConsecutiveHitsBonus = True
        # Originally this was true, but I decided to disable it because the one of
        # my friends (a professional game designer) said "In the game designing
        # theory, subtracting scores is a totally bad idea!". And the penalty was
        # very irritating, actually. lol!
        self.allowConsecutiveMissesBonus = False
        self.allowLevelupBonus = True
        self.name = "Base"
        self.paused = False

    def initialize(self, field):
        self.field = field

    def frameUpdate(self):
        pass

    def calculateNextLevelup(self):
        """
        Calculates the number of enemies that should be defeated in this mode. This function implements the default formula.
        """
        if self.field.level == 1:
            return 2
        r = int(1 + (self.field.level * self.field.level * 0.25))
        if r > 60:
            r = 60
        return r

    def calculateEnemyDefeatScore(self, speed, y):
        """Calculates score by enemy defeat. Since the object references are not organized, I just give up on refactoring it and gather information in a dirty way, if needed. Receives speed and y coors from the defeated enemy."""
        score = (1000 - speed) * (y + 1) * (0.5 + (0.5 * self.field.level)) * 0.1
        if self.field.player.penetrate:
            score = score * 2.0
        return score

    def getDefeatMessage(self, speed, y):
        """Generates log message for enemy defeat."""
        if self.field.player.penetrate:
            return _("Hit! (speed %(speed)d, distance %(distance)d, penetration bonus added)") % {"speed": 900 - speed, "distance": y}
        else:
            return _("Hit! (speed %(speed)d, distance %(distance)d)") % {"speed": 900 - speed, "distance": y}
        # end penetration bonus?

    def getShrinkMultiplier(self):
        """
                Defines the multiplier amount of the shrink item effect in this mode, Default is 0.5 (half length).

                :rtype multiplier: float
        """
        return 0.5

    def getSlowDownMultiplier(self):
        """
                Defines the multiplier amount of the slow down item effect in this mode, Default is 2.0 (2x motion time).

                :rtype multiplier: float
        """
        return 2.0

    def onEnemyDefeated(self):
        """Called when the player defeated an enemy."""
        pass

    def onItemObtained(self):
        """Called when the player got an item."""
        pass

    def getName(self):
        """
        Retrieves the name of this mode. Normal, arcade or classic. There may be more future modes.

        :rtype: str
        """
        return self.name

    def setPaused(self, p):
        """Pauses / resumes this mode handler."""
        pass

    def getModeSpecificResults(self):
        """Can set the modes's specific result data in the game end. Return the array of strings to show at the result screen, otherwise, return an empty array."""
        return []

    def getModeSpecificResultsForScoreboard(self):
        """Can set the modes's specific result data when sending score. Return the string to be shown to the scoreboard, otherwise, return an empty string."""
        return ""


class NormalModeHandler(ModeHandlerBase):
    def __init__(self):
        super().__init__()
        self.name = ALL_MODES_STR[0]

    def initialize(self, field):
        super().initialize(field)


class ArcadeModeHandler(ModeHandlerBase):
    def __init__(self):
        super().__init__()
        self.name = ALL_MODES_STR[1]

    def initialize(self, field):
        super().initialize(field)
        self.itemComingTimer = window.Timer()
        self.resetItemComingTimer()
        self.itemShowerTimer = window.Timer()
        self.resetItemShower()

    def frameUpdate(self):
        if self.itemShowerTimer.elapsed >= self.itemShowerTime:
            self.triggerItemShower()
        if self.itemComingTimer.elapsed >= self.itemComingTime:
            self.spawnItem()

    def setPaused(self, p):
        if p == self.paused:
            return
        self.paused = p
        self.itemComingTimer.setPaused(p)
        self.itemShowerTimer.setPaused(p)
    # end setPaused

    def triggerItemShower(self):
        self.spawnItem()
        self.itemShowerCount -= 1
        if self.itemShowerCount == 0:
            self.resetItemShower()
        else:
            self.itemShowerTime = 150
            self.itemShowerTimer.restart()

    def resetItemShower(self):
        self.itemShowerTime = random.randint(70000, 150000)
        self.itemShowerCount = random.randint(3, 6)

    def spawnItem(self):
        spd = random.randint(100, 800)
        t = itemConstants.TYPE_NASTY if random.randint(1, 100) <= spd / 10 else itemConstants.TYPE_GOOD
        ident = self.selectNastyItem() if t == item.TYPE_NASTY else random.randint(0, item.GOOD_MAX)
        i = item.Item()
        i.initialize(self.field, random.randint(0, self.field.x - 1), spd, t, ident)
        self.field.items.append(i)
        self.resetItemComingTimer()

    def selectNastyItem(self):
        """Prevents shrink from appearing when the player already has 2 shrink effects."""
        shrinks = len([e for e in self.field.player.itemEffects if e.name ==
                       itemConstants.NAMES[itemConstants.TYPE_NASTY][itemConstants.NASTY_SHRINK]])
        while(True):
            ret = random.randint(0, itemConstants.NASTY_MAX)
            if ret == itemConstants.NASTY_SHRINK and shrinks == 2:
                continue
            break
        return ret

    def resetItemComingTimer(self):
        self.itemComingTimer.restart()
        self.itemComingTime = random.randint(0, 60000)


class ClassicModeHandler(ModeHandlerBase):
    def __init__(self):
        super().__init__()
        # disable bonuses
        self.allowConsecutiveHitsBonus = False
        self.allowConsecutiveMissesBonus = False
        self.allowLevelupBonus = False
        self.name = ALL_MODES_STR[2]

    def calculateNextLevelup(self):
        """
        This function provides classic mode specific formula.
        """
        return int((2 + self.field.level) * 0.7)


class BurdenModeHandler(ModeHandlerBase):
    def __init__(self):
        super().__init__()
        # disable bonuses
        self.allowConsecutiveHitsBonus = False
        self.allowConsecutiveMissesBonus = False
        self.allowLevelupBonus = False
        self.name = ALL_MODES_STR[3]
        self.bonusCounters = []
        self.highestBoost = 1.0

    def initialize(self, field):
        super().initialize(field)
        self.itemComingTimer = window.Timer()
        self.resetItemComingTimer()
        self.itemShowerTimer = window.Timer()
        self.resetItemShower()

    def calculateEnemyDefeatScore(self, speed, y):
        """Uses completely different formula for burden mode."""
        boost = math.pow(1.45 + (self.field.level * 0.05), len(self.field.player.itemEffects))
        # Update highest boost here
        if boost > self.highestBoost:
            self.highestBoost = boost
        # end update highest boost
        return boost * (1000 - speed) * math.pow(self.field.level, 2) / 5

    def getDefeatMessage(self, speed, y):
        boost = "%.1f" % math.pow(1.45 + (self.field.level * 0.05), len(self.field.player.itemEffects))
        return _("Hit! (speed %(speed)d, burden %(burden)d, %(boost)sx boost)") % {
            "speed": 900 - speed, "burden": len(self.field.player.itemEffects), "boost": boost}

    def getShrinkMultiplier(self):
        return 0.75

    def getSlowDownMultiplier(self):
        return 1.5

    def frameUpdate(self):
        for elem in self.bonusCounters[:]:
            if not elem.active:
                self.bonusCounters.remove(elem)
                continue
            # end cleanup
            elem.frameUpdate()
        # end update bonus counters
        if self.itemShowerTimer.elapsed >= self.itemShowerTime:
            self.triggerItemShower()
        if self.itemComingTimer.elapsed >= self.itemComingTime:
            self.spawnItem()
            self.resetItemComingTimer()

    def setPaused(self, p):
        if p == self.paused:
            return
        self.paused = p
        self.itemComingTimer.setPaused(p)
        self.itemShowerTimer.setPaused(p)
    # end setPaused

    def triggerItemShower(self):
        self.spawnItem()
        self.itemShowerCount -= 1
        if self.itemShowerCount == 0:
            self.resetItemShower()
        else:
            self.itemShowerTime = 150
            self.itemShowerTimer.restart()

    def resetItemShower(self):
        self.itemShowerTime = random.randint(70000, 150000)
        self.itemShowerCount = random.randint(3, 6)

    def spawnItem(self):
        spd = random.randint(100, 800)
        t = itemConstants.TYPE_NASTY
        ident = self.selectNastyItem()
        i = item.Item()
        i.initialize(self.field, random.randint(0, self.field.x - 1), spd, t, ident)
        self.field.items.append(i)

    def selectNastyItem(self):
        """Prevents shrink from appearing when the player already has 3 shrink effects."""
        shrinks = len([e for e in self.field.player.itemEffects if e.name ==
                       itemConstants.NAMES[itemConstants.TYPE_NASTY][itemConstants.NASTY_SHRINK]])
        while(True):
            ret = random.randint(0, itemConstants.NASTY_MAX)
            if ret == itemConstants.NASTY_SHRINK and shrinks == 3:
                continue
            break
        return ret

    def resetItemComingTimer(self):
        self.itemComingTimer.restart()
        self.itemComingTime = random.randint(0, 60000)

    def onEnemyDefeated(self):
        effects = len(self.field.player.itemEffects)
        if effects > 0:
            bc = bonusCounter.BonusCounter()
            bc.initialize()
            bc.start(effects)
            self.bonusCounters.append(bc)
        # end append bonus counter

    def onItemObtained(self):
        self.spawnItem()

    def getModeSpecificResults(self):
        boost = "%.1f" % self.highestBoost
        return [
            _("Highest boost: %(boost)sx") % {"boost": boost}
        ]

    def getModeSpecificResultsForScoreboard(self):
        boost = "%.1f" % self.highestBoost
        return "%(boost)sx highest boost" % {"boost": boost}


def getModeHandler(mode):
    """Receives a mode in string and returns the associated modeHandler object without initializing it.

    :param mode: Mode.
    :type mode: str
    """
    if mode == ALL_MODES_STR[0]:
        return NormalModeHandler()
    if mode == ALL_MODES_STR[1]:
        return ArcadeModeHandler()
    if mode == ALL_MODES_STR[2]:
        return ClassicModeHandler()
    if mode == ALL_MODES_STR[3]:
        return BurdenModeHandler()
    return None
