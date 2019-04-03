# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import platform
import sys
import shutil
import common

win=True
if platform.system() == 'Darwin':
	win=False

print("win=%s, cwd=%s" % (win, os.getcwd()))
sys.exit()
PROJECT = "ss"  # Change this line accordingly
PYTHON_PATH="C:/python37"#Windows only

if not os.path.exists("data"):
  print("Error: no data folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
  sys.exit()

print("Building %s. This will take several minutes. Please wait..." % PROJECT)
if win:
	cmd="nuitka --follow-imports --windows-disable-console --standalone --mingw64 --include-plugin-directory=sound_lib/lib/x64 %s.py" % (PROJECT)
else:
	cmd="python3 -m nuitka --follow-imports --standalone --include-plugin-directory=sound_lib/lib/x64 %s.py" % (PROJECT)
common.run(cmd, sh=True)
if win:
	print("Copying pythoncom37.dll...")
	shutil.copyfile("%s/Lib/site-packages/pywin32_system32/pythoncom37.dll" % (PYTHON_PATH), "%s.dist/pythoncom37.dll" % PROJECT)

print("Copying sound_lib dlls...")
shutil.copytree("sound_lib/lib/x64", "%s.dist/sound_lib/lib/x64" % PROJECT)
common.mkdir("%s.dist/accessible_output2" % PROJECT)
print("Copying accessible_output2 dlls...")
shutil.copytree("accessible_output2/lib", "%s.dist/accessible_output2/lib" % PROJECT)
print("Copying data files...")
shutil.copytree("data", "%s.dist/data" % (PROJECT),
                ignore=shutil.ignore_patterns("options.dat"))
print("Done!")
