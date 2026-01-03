[app]

# (str) Title of your application
# change this in your own build
# This is demo-only.
title = Altrus Simulator

# (str) Package name
package.name = altrus_simulator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.altrus

# (str) Source code where the main.py live
source.dir = .

# (str) The name of the main python file without the .py extension
entrypoint = main

# (list) Application requirements
requirements = python3,kivy

# (list) Permissions
android.permissions = INTERNET

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (str) Android API to use
android.api = 33

# (str) Minimum API required
android.minapi = 23

# (str) Enable androidX
android.enable_androidx = True

[buildozer]

# (str) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 1

# (str) Location where build output will be placed
build_dir = .build

# (str) Download directory for android dependencies
bin_dir = bin
