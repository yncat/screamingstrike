# -*- coding: utf-8 -*-
#Screaming Strike startup file
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
#See SsAppMain.py for application entry point
import sys
import os
import buildSettings
import platform_utils.paths
if platform_utils.paths.is_mac and platform_utils.paths.is_frozen(): os.chdir("../Resources")
from ssAppMain import *

def main():
	app=ssAppMain()
	app.initialize()
	app.run()

#global schope

if __name__ == "__main__": main()