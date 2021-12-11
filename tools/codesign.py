import subprocess

cmdlist = ["codesign", "-f", "-s", "Yukio Nozawa", "-v", "--deep", "--timestamp", "--entitlements", "entitlements.plist", "-o", "runtime", "dist/ss.app"]
subprocess.run(cmdlist)
