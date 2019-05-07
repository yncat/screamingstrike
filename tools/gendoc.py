# -*- coding: utf-8 -*-
# class API auto generation using sphinx
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import common

win=True
if platform.system() == 'Darwin':
	win=False

print("win=%s, cwd=%s" % (win, os.getcwd()))
common.run("sphinx-apidoc -F -o docs/api .")
common.run("sphinx-build -b html docs/api docs/api/_build")
