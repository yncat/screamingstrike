# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import platform
import sys
import shutil
import glob
import common

def dopackage():
	if win:
		print("Creating installer exe")
		f=open("_build.bat","w")
		f.write("WinRAR a -cfg- -ed -ep1 -k -m5 -r -sfx \"-ztools\\rar_options.txt\" \"%s.exe\" \"dist\\%s\\*\"" % (PROJECT_FULL_NAME, PROJECT))
		f.close()
		common.run("cmd /c _build.bat")
		os.remove("_build.bat")
	if not win:
		print("Creating image dmg")
		os.rename("dist/"+PROJECT+".app","dist/"+PROJECT_FULL_NAME+".app")
		os.remove("dist/%s" % PROJECT)
		common.run("hdiutil create -volname %s -srcfolder ./dist -ov -format UDZO %s.dmg" % (PROJECT_FULL_NAME, PROJECT_FULL_NAME))

win=True
if platform.system() == 'Darwin':
	win=False

#pywin32 rebuilding (Carter)
genpy_path=os.path.join(os.environ["temp"], "gen_py")
if os.path.isdir(genpy_path):
	print("Deleting pywin32 cach...")
	shutil.rmtree(genpy_path)
#end rebuilding

print("win=%s, cwd=%s" % (win, os.getcwd()))
PROJECT = "ss"  # Change this line accordingly
PROJECT_FULL_NAME="screamingStrike2"
PYTHON_PATH="D:\softs\Python37-32"#Windows only

if not os.path.exists("data"):
  print("Error: no data folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
  sys.exit()

print("Building %s. This will take several minutes. Please wait..." % PROJECT)

if "--skip-compile" in sys.argv:
	print("Skipping to packaging")
	dopackage()
	print("Done!")
	sys.exit()

copydir=""

if win:
	cmd="pyinstaller --windowed %s.py" % (PROJECT)
	copydir="dist/%s" % PROJECT
else:
	cmd="pyinstaller --windowed --onefile --osx-bundle-identifier com.nyanchanGames.%s %s.py" % (PROJECT_FULL_NAME, PROJECT)
	copydir="dist/%s.app/Contents/Resources" % PROJECT

common.run(cmd, sh=win)#win uses shell=true and mac doesn't
if not win:
	print("Copying sound_lib dlls...")
	shutil.copytree("sound_lib/lib", "%s/sound_lib/lib" % copydir)
	common.mkdir("%s/accessible_output2" % copydir)
	print("Copying accessible_output2 dlls...")
	shutil.copytree("accessible_output2/lib", "%s/accessible_output2/lib" % copydir)
#end copies for mac
print("Copying data files...")
shutil.copytree("data", "%s/data" % (copydir),
                ignore=shutil.ignore_patterns("options.dat","collection.dat","stats.dat"))
print("Copying locale files...")
shutil.copytree("locale", "%s/locale" % (copydir))
print("Copying readme")
readmes=glob.glob("readme_*.txt")
for elem in readmes:
	shutil.copyfile(elem, "%s/%s" % (copydir, elem))

print("Copying changelog")
changelogs=glob.glob("changelog_*.txt")
for elem in changelogs:
	shutil.copyfile(elem, "%s/%s" % (copydir, elem))

if win:
	print("Renaming to play.exe")
	os.rename(copydir+"/"+PROJECT+".exe",copydir+"/play.exe")
dopackage()
print("Done!")
