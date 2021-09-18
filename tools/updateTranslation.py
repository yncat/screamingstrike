# -*- coding: utf-8 -*-
# Translation update Tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import os
import subprocess
import glob
import shutil

if not os.path.exists("locale"):
    print("Error: no locale folder found. Your working directory must be the root of the ss project. You shouldn't cd to tools and run this script.")
    sys.exit()
if not os.path.exists("tools/xgettext.exe") or not os.path.exists("tools/msgmerge.exe"):
    print("Error: xgettext or msgmerge is missing.")
    sys.exit()

langs = []
for elem in glob.glob("locale/*"):
    if os.path.isdir(elem):
        langs.append(os.path.basename(elem))

print("Detected languages:")
for l in langs:
    print(l)

files = glob.glob("*.py")
print("Detected files:")
for f in files:
    print(f)

print("Updating the base dictionary(pot)")
subprocess.call(("tools\\xgettext.exe -p locale --from-code utf-8 --package-name=screamingStrike %s" % (" ".join(files))).split())
for l in langs:
    if os.path.exists("locale/%s/LC_MESSAGES/messages.po" % (l)):
        print("Merging %s" % l)
        subprocess.call(("tools\\msgmerge.exe -U locale/%s/LC_MESSAGES/messages.po locale/messages.po" % (l)).split())
    else:
        print("Creating %s" % l)
        if not os.path.exists("locale/%s/LC_MESSAGES" % l):
            print("Creating LC_MESSAGES")
            os.mkdir("locale/%s/LC_MESSAGES" % l)
        shutil.copyfile("locale/messages.po", "locale/%s/LC_MESSAGES/messages.po" % l)
print("Done")
sys.exit(0)
