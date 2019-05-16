# -*- coding: utf-8 -*-
# Simple crossplatform dialog
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)

import platform
import ctypes
import subprocess
import re
def dialog(title,message):
	if platform.system()=="Windows":
		ctypes.windll.user32.MessageBoxW(0,message,title,0x00000040)
	else:
		str="display dialog \"%s\" with title \"%s\" with icon note buttons {\"OK\"}" %(re.sub(r'"\''," ",message), re.sub(r'"\''," ",title))#escaping ' and " on mac
		subprocess.call("osascript -e '{}'".format(str), shell=True)
