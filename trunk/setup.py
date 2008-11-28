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
    import go
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

doclines = __doc__.split("\n")
if sys.platform == "win32":
    scripts = ["lib\\go.py", "bin\\go.bat"]
else:
    scripts = ["bin/go"]

setup(
    name="go",
    version=go.__version__,
    maintainer="Trent Mick",
    maintainer_email="trentm@gmail.com",
    url="http://code.google.com/p/python-markdown2/",
    license="http://www.opensource.org/licenses/mit-license.php",
    platforms=["any"],
    py_modules=["go"],
    package_dir={"": "lib"},
    scripts=scripts,
    description=doclines[0],
    classifiers=filter(None, classifiers.split("\n")),
    long_description="\n".join(doclines[2:]),
)

