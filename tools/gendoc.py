# -*- coding: utf-8 -*-
# class API auto generation using sphinx
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import common

common.run([
    "sphinx-build",
    "-b",
    "html",
    "docs/api",
    "docs/api/_build"
])
