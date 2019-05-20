# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import platform
import sys
import shutil
import glob
import common

win=True
if platform.system() == 'Darwin':
	win=False

print("win=%s, cwd=%s" % (win, os.getcwd()))
PROJECT = "ss"  # Change this line accordingly
PROJECT_FULL_NAME="screamingStrike2"
PYTHON_PATH="C:/python37"#Windows only

if not os.path.exists("data"):
  print("Error: no data folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
  sys.exit()

print("Building %s. This will take several minutes. Please wait..." % PROJECT)
copydir=""

if win:
	cmd="nuitka --follow-imports --windows-disable-console --standalone --mingw64 --include-plugin-directory=sound_lib/lib/x64 %s.py" % (PROJECT)
	copydir="%s.dist" % PROJECT
else:
	cmd="pyinstaller --windowed --onefile --osx-bundle-identifier com.nyanchanGames.%s %s.py" % (PROJECT, PROJECT)
	copydir="dist/%s.app/Contents/Resources" % PROJECT

common.run(cmd, sh=win)#win uses shell=true and mac doesn't
if win:
	print("Copying pythoncom37.dll...")
	shutil.copyfile("%s/Lib/site-packages/pywin32_system32/pythoncom37.dll" % (PYTHON_PATH), "%s.dist/pythoncom37.dll" % PROJECT)

print("Copying sound_lib dlls...")
shutil.copytree("sound_lib/lib/x64", "%s/sound_lib/lib/x64" % copydir)
common.mkdir("%s/accessible_output2" % copydir)
print("Copying accessible_output2 dlls...")
shutil.copytree("accessible_output2/lib", "%s/accessible_output2/lib" % copydir)
print("Copying data files...")
shutil.copytree("data", "%s/data" % (copydir),
                ignore=shutil.ignore_patterns("options.dat","collection.dat","stats.dat"))
print("Copying locale files...")
shutil.copytree("locale", "%s/locale" % (copydir))
print("Copying readme")
readmes=glob.glob("readme_*.txt")
for elem in readmes:
	shutil.copyfile(elem, "%s/%s" % (copydir, elem))

if win:
	print("Renaming to play.exe")
	os.rename(PROJECT+".dist/"+PROJECT+".exe",PROJECT+".dist/play.exe")
if win:
	print("Creating installer exe")
	common.run("WinRAR a -cfg- -ed -ep1 -k -m5 -r -sfx \"-ztools\\rar_options.txt\" \"%s.exe\" \"%s.dist\\*\"" % (PROJECT_FULL_NAME, PROJECT), shell=True)
if not win:
	print("Creating image dmg")
	os.remove("dist/%s" % PROJECT)
	common.run("hdiutil create -volname %s -srcfolder ./dist -ov -format UDZO %s.dmg" % PROJECT_FULL_NAME)

print("Done!")
