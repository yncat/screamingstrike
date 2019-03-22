# -*- coding: utf-8 -*-
# app build tool
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import subprocess
import shutil

ROOT_FILE = "ss.py"  # Change this line accordingly

if not os.path.exists("locale"):
  print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
  sys.exit()

print("Building the project. This will take several minutes. Please wait...")
subprocess.call(
    ("nuitka --follow-imports --standalone --mingw64 --windows-disable-console %s" % ROOT_FILE).split(), shell=True)
shutil.copytree("locale/", "screamingStrike.dist/locale",
                ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
print("Done!")
