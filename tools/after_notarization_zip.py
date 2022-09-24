import os
import common

PROJECT_FULL_NAME = "screamingStrike2"

os.chdir("build")

common.run([
    "xcrun",
    "stapler",
    "staple",
    "dist/%s.app" % (PROJECT_FULL_NAME)
])

common.run([
    "hdiutil",
    "create",
    "-volname",
    PROJECT_FULL_NAME,
    "-srcfolder",
    "./dist",
    "-ov",
    "-format",
    "UDZO",
    "%s.dmg" % (PROJECT_FULL_NAME)
])

common.run([
    "codesign",
    "-s",
    "Developer ID Application: Yukio Nozawa",
    "--timestamp",
    "%s.dmg" % (PROJECT_FULL_NAME)
])
