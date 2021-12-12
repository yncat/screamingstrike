import os
import common

PROJECT_FULL_NAME = "screamingStrike2"

os.chdir("build")

common.run([
    "xcrun",
    "stapler",
    "staple",
    "%s.dmg" % (PROJECT_FULL_NAME)
])
