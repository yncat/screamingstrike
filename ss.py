# -*- coding: utf-8 -*-
#Screaming Strike startup file
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#See SsAppMain.py for application entry point
import sys
import os
import platform
if platform.system()=="Darwin": os.setcwd("../Resources")
print(os.getcwd())
from ssAppMain import *

def main():

#	sys.stderr = open('data/errorLog.txt', 'w') # uncomment this line when releasing
	app=ssAppMain()
	app.initialize()
	app.run()

#global schope

if __name__ == "__main__": main()