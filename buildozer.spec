[app]
title = NEXA KIDS AFRICA
package.name = nexakids
package.domain = org.nexa
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .github, bin, .buildozer, __pycache__
source.exclude_patterns = generer_emojis.py
version = 3.0
requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.0,plyer,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
