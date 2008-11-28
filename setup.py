#!/usr/bin/env python
# Copyright (c) 2002-2008 ActiveState Software
# Author: Trent Mick (trentm@gmail.com)

"""Quick directory changing (super-cd)

'go' is a simple command line script to simplify jumping between
directories in the shell. You can create shortcut names for commonly
used directories and invoke 'go <shortcut>' to switch to that directory
-- among other little features.
"""

import os
import sys
from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
try:
    import markdown2
finally:
    del sys.path[0]

#TODO: Operating System classifiers
#  Operating System :: OS Independent
classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

if sys.version_info < (2, 3):
    # Distutils before Python 2.3 doesn't accept classifiers.
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)


#---- support routines

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
            # Note: Convert to string because distutils apparently
            # cannot handle unicode paths.
            dqsdDir = str(_getDQSDInstallDir())
            df.append( (os.path.join(dqsdDir, "localsearches"),
                        ["go.xml"]) )
        except (EnvironmentError, UnicodeError):
            pass
    return df


#---- setup mainline

doclines = __doc__.split("\n")
script = (sys.platform == "win32" and "lib\\markdown2.py" or "bin/markdown2")

setup(name="go",
      version=_getVersion(),
      description="Quick directory changing (super-cd)",
      author="Trent Mick",
      author_email="trentm@gmail.com",
      url="http://code.google.com/p/go-tool/",
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
setup(
    name="go",
    version=go.__version__,
    maintainer="Trent Mick",
    maintainer_email="trentm@gmail.com",
    url="http://code.google.com/p/python-markdown2/",
    license="http://www.opensource.org/licenses/mit-license.php",
    platforms=["any"],
    py_modules=["markdown2"],
    package_dir={"": "lib"},
    scripts=scripts,
    description=doclines[0],
    classifiers=filter(None, classifiers.split("\n")),
    long_description="\n".join(doclines[2:]),
)

