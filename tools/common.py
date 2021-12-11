# -*- coding: utf-8 -*-
# tools common module
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import subprocess
import shutil


def run(cmdlist,):
    """Runs a specific command."""
    ret = subprocess.run(cmdlist)
    if ret.returncode != 0:
        sys.stderr.write(
            "Error: %s returned non-zero exit code (%d)" % (cmdlist, ret.returncode))
        sys.exit(ret.returncode)


def mkdir(fld):
    """Makes a directory. It skips if it already exists. """
    sys.stdout.write("Checking directory: %s ... " % fld)
    if os.path.isdir(fld):
        sys.stdout.write("exists\n")
        return
    else:
        os.mkdir(fld)
        sys.stdout.write("created\n")
