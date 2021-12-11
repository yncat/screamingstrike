# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019-2021 Yukio Nozawa <personal@nyanchangames.com>
import os
import platform
import sys
import shutil
import subprocess
import glob
import common


def clearPreviousBuild():
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("dist"):
        shutil.rmtree("dist")


def copyBeforeBuild():
    os.mkdir("build")
    for file in glob.glob("*.*"):
        shutil.copyfile(file, os.path.join("build", file))
    deletefiles = [
        "requirements-win.txt",
        "requirements-mac.txt",
        "result.txt"
    ]
    for file in deletefiles:
        os.remove(os.path.join("build", file))
    copydirs = [
        "data",
        "locale",
        "public",
        "sound_lib",
        "platform_utils",
        "libloader",
        "accessible_output2"
    ]
    for dir in copydirs:
        shutil.copytree(dir, os.path.join("build", dir))
    shutil.copyfile(os.path.join("tools", "rar_options.txt"),
                    os.path.join("build", "rar_options.txt"))


def removeUnnecessaryFilesForMac():
    shutil.rmtree("build/sound_lib/lib/x86")
    libs = glob.glob("build/sound_lib/lib/x64/*.dll")
    libs.extend(glob.glob("build/sound_lib/lib/x64/*.so"))
    for lib in libs:
        os.remove(lib)
    shutil.rmtree("build/accessible_output2/lib")


def dopackage():
    if win:
        print("Creating installer exe")
        f = open("_build.bat", "w")
        f.write("WinRAR a -cfg- -ed -ep1 -k -m5 -r -sfx \"-zrar_options.txt\" \"%s.exe\" \"dist\\%s\\*\"" %
                (PROJECT_FULL_NAME, PROJECT))
        f.close()
        common.run("cmd /c _build.bat")
        os.remove("_build.bat")
    if not win:
        print("codesigning...")
        subprocess.run([
            "codesign",
            "-f",
            "-s",
            "Yukio Nozawa",
            "-v",
            "--deep",
            "--timestamp",
            "--entitlements",
            "entitlements.plist",
            "-o",
            "runtime",
            "dist/%s.app" % PROJECT
        ])
        os.rename(os.path.join("dist", PROJECT + ".app"),
                  os.path.join("dist", PROJECT_FULL_NAME+".app"))
        os.remove(os.path.join("dist", PROJECT))
        print("Creating image dmg")
        common.run("hdiutil create -volname %s -srcfolder ./dist -ov -format UDZO %s.dmg" %
                   (PROJECT_FULL_NAME, PROJECT_FULL_NAME))


win = True
if platform.system() == 'Darwin':
    win = False

if win:
    # pywin32 rebuilding (Carter)
    genpy_path = os.path.join(os.environ["temp"], "gen_py")
    if os.path.isdir(genpy_path):
        print("Deleting pywin32 cach...")
        shutil.rmtree(genpy_path)
# end rebuilding

print("win=%s, cwd=%s" % (win, os.getcwd()))
PROJECT = "ss"  # Change this line accordingly
PROJECT_FULL_NAME = "screamingStrike2"
PYTHON_PATH = r"D:\softs\Python37-32"  # Windows only

if not os.path.exists("data"):
    print("Error: no data folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
    sys.exit()

copydir = ""

clearPreviousBuild()  # Copy all files to build directory first
copyBeforeBuild()
if not win:
    removeUnnecessaryFilesForMac()

os.chdir("build")

if win:
    cmd = "pyinstaller --windowed %s.py" % (PROJECT)
    copydir = "dist/%s" % PROJECT
else:
    cmd = "pyinstaller --windowed --onefile --osx-bundle-identifier com.nyanchanGames.%s %s.py" % (
        PROJECT_FULL_NAME, PROJECT)
    copydir = "dist/%s.app/Contents/Resources" % PROJECT

common.run(cmd, sh=win)  # win uses shell=true and mac doesn't
if not win:
    print("Copying sound_lib dynamic libraries...")
    shutil.copytree("sound_lib/lib", "%s/sound_lib/lib" % copydir)
# end copies for mac
print("Copying data files...")
shutil.copytree("data", "%s/data" % (copydir),
                ignore=shutil.ignore_patterns("options.dat", "collection.dat", "stats.dat"))
print("Copying locale files...")
shutil.copytree("locale", "%s/locale" % (copydir))
print("Copying other public files")
for file in glob.glob("public/*.*"):
    basename = os.path.basename(file)
    shutil.copyfile(file, os.path.join(copydir, basename))

if win:
    print("Renaming to play.exe")
    os.remove(copydir + "/" + PROJECT + ".exe.manifest")
    os.rename(copydir + "/" + PROJECT + ".exe", copydir + "/play.exe")
dopackage()
print("Done!")
