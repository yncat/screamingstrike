# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import shutil
import common

PROJECT = "ss"  # Change this line accordingly
PYTHON_PATH="C:/python37"

if not os.path.exists("data"):
  print("Error: no data folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
  sys.exit()

print("Building %s. This will take several minutes. Please wait..." % PROJECT)
common.run("nuitka --follow-imports --windows-disable-console --standalone --mingw64 --include-plugin-directory=sound_lib/lib/x64 %s.py" % (PROJECT), sh=True)
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
