# -*- coding: utf-8 -*-
# Screaming Strike item constant values
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
STATE_ALIVE = 0
STATE_BROKEN = 1
STATE_SHOULDBEDELETED = 2

BASE_EFFECT_TIME = 15000
TYPE_NASTY = 0
TYPE_GOOD = 1

NASTY_SHRINK = 0
NASTY_BLURRED = 1
NASTY_SLOWDOWN = 2
NASTY_MAX = 2

GOOD_MEGATONPUNCH = 0
GOOD_BOOST = 1
GOOD_PENETRATION = 2
GOOD_DESTRUCTION = 3
GOOD_EXTRALIFE = 4
GOOD_MAX = 4
NAMES = {}
NAMES[TYPE_NASTY] = {NASTY_SHRINK: "Shrink",
   NASTY_BLURRED: "Blurred", NASTY_SLOWDOWN: "Slow down"}
NAMES[TYPE_GOOD] = {GOOD_MEGATONPUNCH: "Megaton punch", GOOD_BOOST: "Boost",
    GOOD_PENETRATION: "Penetration", GOOD_DESTRUCTION: "Destruction", GOOD_EXTRALIFE: "Extra life"}

