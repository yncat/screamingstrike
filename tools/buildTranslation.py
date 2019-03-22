# -*- coding: utf-8 -*-
# Translation building Tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import sys
import os
import subprocess
import glob
import shutil

if not os.path.exists("locale"):
  print("Error: no locale folder found. Your working directory must be the root of the falcon project. You shouldn't cd to tools and run this script.")
  sys.exit()
if not os.path.exists("tools/msgfmt.exe"):
  print("Error: msgfmt is missing.")
  sys.exit()

langs = []
for elem in glob.glob("locale/*"):
  if os.path.isdir(elem):
    langs.append(os.path.basename(elem))

print("Detected languages:")
for l in langs:
  print(l)

print("Building mo files")
for l in langs:
  subprocess.call(
      ("tools\\msgfmt.exe -o locale/%s/LC_MESSAGES/messages.mo locale/%s/LC_MESSAGES/messages.po" % (l, l)).split())
print("Done")
sys.exit(0)
