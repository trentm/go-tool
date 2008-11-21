#!/usr/bin/env python
# Copyright (c) 2002-2005 ActiveState Corp.
# Author: Trent Mick (TrentM@ActiveState.com)

"""Distutils setup script for 'go'."""

import sys
import os
from distutils.core import setup


#---- support routines

def _getVersion():
    import go
    return go.__version__

def _getBinDir():
    """Return the current Python's bindir."""
    if sys.platform.startswith("win"):
        bindir = sys.prefix
    else:
        bindir = os.path.join(sys.prefix, "bin")
    return bindir

def _getBinFiles():
    if sys.platform.startswith("win"):
        return ["go.bat", "gow.exe", "go.py"]
    else:
        return []

def _getScripts():
    if sys.platform.startswith("win"):
        return []
    else:
        return ["go"]

if sys.platform.startswith("win"):
    from win32com.shell import shellcon, shell
    # win32com.shellcon is missing some defines
    shellcon.CSIDL_PROGRAM_FILES = 0x26
    def _getDQSDInstallDir():
        programFiles = shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAM_FILES,
                                             0, 0)
        dqsdDir = os.path.join(programFiles, "Quick Search Deskbar")
        if not os.path.isdir(dqsdDir):
            raise EnvironmentError("Could not determine where Dave's Quick "
                                   "Search Deskbar is installed.")
        return dqsdDir

def _getDataFiles():
    df = []
    df.append( (_getBinDir(), _getBinFiles()) )
    if sys.platform.startswith("win"):
        # Dave Quick Search Deskbar integration.
        try:
            #XXX Convert to string because distutils apparently cannot
            #    handle unicode paths.
            dqsdDir = str(_getDQSDInstallDir())
            df.append( (os.path.join(dqsdDir, "localsearches"),
                        ["go.xml"]) )
        except (EnvironmentError, UnicodeError):
            pass

    return df


#---- setup mainline

setup(name="go",
      version=_getVersion(),
      description="Quick directory changing",
      author="Trent Mick",
      author_email="TrentM@ActiveState.com",
      url="http://trentm.com/projects/go/",
      license="MIT License",
      platforms=["Windows", "Linux", "Mac OS X", "Unix"],
      long_description="""\
'go' is a simple command line script to simplify jumping between
directories in the shell. You can create shortcut names for commonly
used directories and invoke 'go <shortcut>' to switch to that directory
-- among other little features.
""",
      keywords=["directory", "cd", "go", "dqsd",
                "Dave's Quick Search Deskbar", "folder"],

      scripts=_getScripts(),
      data_files=_getDataFiles(),
     )

