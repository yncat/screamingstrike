# -*- coding: utf-8 -*-
#Screaming Strike startup file
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
#See SsAppMain.py for application entry point
import sys
import shutil
import os
import platform_utils.paths
import traceback
if platform_utils.paths.is_mac and platform_utils.paths.is_frozen(): os.chdir(platform_utils.paths.embedded_data_path())
import buildSettings
from ssAppMain import *

def main():
	app=ssAppMain()
	app.initialize()
	app.run()

def exchandler(type, exc, tb):
	f=open("data/errorLog.txt", "w")
	f.writelines(traceback.format_exception(type, exc, tb))
	f.close()
	dialog.dialog("Error", "An error occured. Please send error-log.txt, found in the data directory of wherever you are running the game, to the developer.")
	sys.exit()

#global schope
sys.excepthook=exchandler
genpy_path=os.path.join(os.environ["temp"], "gen_py")
if os.path.isdir(genpy_path):
	shutil.rmtree(genpy_path)
#end rebuilding

if __name__ == "__main__": main()