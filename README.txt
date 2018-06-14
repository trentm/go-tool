go -- quick directory switching
===============================

Home            : https://github.com/trentm/go-tool
License         : MIT (see LICENSE.txt)
Platforms       : Windows, Linux, Mac OS X, Unix
Current Version : 1.2.2
Dev Status      : mature
Requirements    : Python >= 2.4 and Python 3

Why go?
-------

`go` is a small command for changing directories quickly.
Typically you have a set of directories that you work in.  Typing out
the names of those dirs in full can be tedious.  `go` allows you to
give a shortcut name for a directory, say `ko` for
`D:\trentm\main\Apps\Komodo-devel`, and do the following:

    C:\> go ko
    D:\trentm\main\Apps\Komodo-devel>

and

    C:\> go ko/test
    D:\trentm\main\Apps\Komodo-devel\test>

In addition, go supports resolving unique prefixes of both shortcuts 
and path components.  So the above example could also be written as:

    C:\> go k/t
    D:\trentm\main\Apps\Komodo-devel\test>

This is assuming that no other shortcut starts with "k" and the 
Komodo-devel directory contains no other directory (files are OK)
that starts with "t".

Think of it as a super `cd`. 

`go` is free (MIT License).  Please send any feedback to [Trent
Mick](mailto:trentm@google's mail thing).


Install Notes
-------------

Download the latest (1) `go` source package, (2) unzip it, (3) run
`python setup.py install` in the unzipped directory, and (4) run
`python -m go` to setup the shell driver:

    unzip go-1.2.2.zip
    cd go-1.2.2
    python setup.py install
    python -m go   # to setup shell integration

If your install fails then please visit [the Troubleshooting
FAQ](http://trentm.com/faq.html#troubleshooting-python-package-installation).

Please note that the "go.bat" file for use with Windows cmd.exe does not work
with Powershell.  To use go with Windows Powershell, you must set an environment 
variable to indicate your shell.  You can do this by adding the following line 
to your Powershell profile:

    $env:SHELL = "powershell"

You can then run the following from the Powershell prompt to apply the change
and generate the "go.ps1" wrapper:

    . $profile
    python -m go



Getting Started
---------------

The most common things you'll do with `go` are adding new shortcuts:

    [~/Library/Application Support/Komodo]$ go -a koappdata

listing the shortcuts you've created:

    [~]$ go --list
                        Go Shortcuts
                        ============

    Default shortcuts:
      .                     .
      ..                    ..
      ...                   ../..
      tmp                   /tmp
      ~                     /Users/trentm

    Custom shortcuts:
      cgi-bin               /Library/WebServer/CGI-Executables
      koappdata             /Users/trentm/Library/Application Support/Komodo
      pyinstall             /Library/Frameworks/Python.framework/Versions/2.6
      staging               /Users/trentm/Sites/staging
      www                   /Users/trentm/Sites

and switching to directories using those shortcuts:

    [~]$ go pyinstall
    [/Library/Frameworks/Python.framework/Versions/2.6]$ go www
    [~/Sites]$ 

Run `go --help` for full usage details or just [take a look at the
`go.py` script](go.py):

    $ go --help
    Quick directory changing.

    Usage:
        go <shortcut>[/sub/dir/path]    # change directories
                                        # same as "go -c ..."
        go -c|-o|-a|-d|-s ...           # cd, open, add, delete, set
        go --list [<pattern>]           # list matching shortcuts

    Options:
        -h, --help                      print this help and exit
        -V, --version                   print verion info and exit

        -c, --cd <path>                 cd to shortcut path in shell
        -s, --set <shortcut> <dir>      set a shortcut to <dir>
        -a, --add-current <shortcut>    add shortcut to current directory
        -d, --delete <shortcut>         delete the named shortcut
        -o, --open <path>               open the given shortcut path in
                                        explorer (Windows only)
        -l, --list [<pattern>]          list current shortcuts

    Generally you have a set of directories that you commonly visit.
    Typing these paths in full can be a pain. This script allows one to
    define a set of directory shortcuts to be able to quickly change to
    them. For example, I could define 'ko' to represent
    "D:\trentm\main\Apps\Komodo-devel", then
        C:\> go ko
        D:\trentm\main\Apps\Komodo-devel>
    and
        C:\> go ko/test
        D:\trentm\main\Apps\Komodo-devel\test>

    As well, you can always use some standard shortcuts, such as '~'
    (home) and '...' (up two dirs).

    See <http://trentm.com/projects/go/> for more information.


Change Log
----------

### v1.2.2
- Add Python 3 support

### The following changes were merged from a fork by Peter Geer
(http://hg.skepticats.com/go-posh)
- Add support for Powershell
- Add built-in shortcut "-" pointing to the OLDPWD environment 
  variable (uses built-in shell support in UNIX, emulates in Windows)
- When invoked without any argument, change to home directory
- Resolve unique prefixes of shortcuts
- Resolve unique prefixes of path components.  For example, if "f" is a 
  shortcut for C:\foo and C:\foo\bar\bazz exists, "go f/b/b" will go to it
- Detect home directory in Windows via USERPROFILE
- Make -o option work without win32api bindings and function on other 
  platforms (use FILE_MANAGER env var on UNIX)
- Make -o option apply to current directory when no argument is given
- Add -p option to print the resolved shortcut path rather than cd to it

### v1.2.0
- Add support for "go FOO" falling back to changing to subdirectory
  "FOO" if there is no "FOO" shortcut. Patch from Phil Schwartz.

### v1.1.0
- Move to 'go-tool' Google Code project. (Couldn't use "go" because
  Google Code requires minimum 4 (or 3?) characters for a project
  name.)
- Add automatic setup code to assist with setting up the shell
  integration drivers.

### v1.0.6
- Redo changes to 'function go' that were made in version 1.0.4 so
  that people without my own personal Bash definitions can actually
  use it.

### v1.0.5
- Fix bug where 'go' would fail to switch to a directory with spaces.

### v1.0.4
- Improve Bash 'function go' to fail more gracefully if 'go' is
  not found on the PATH.

### v1.0.3
- Correct information about the suggested Bash "go" function
  definition to avoid a user's possible "which" alias (some RedHat
  systems setup "alias which='type -p'") that can screw things up.

### v1.0.2
- Filter out the stupid FCNTL.py deprecation warning for usage with
  Python 2.3 on Windows.

### v1.0.1
- Ensure the installed 'go' script on non-Windows is executable.

### v1.0.0
- Change version attributes and semantics. Before: had a _version_
  tuple. After: __version__ is a string, __version_info__ is a tuple.

### v0.9.2:
- Fix install on Un*x: 'go' script wasn't in sdist to install

### v0.9.1:
- Find gow.cpp again and get gow.exe into dists to fix installation and
  DQSD integration on Windows.

### v0.9.0:
- Move hosting to trentm.com.
- Improve starter docs a little bit.

### v0.8.2:
- Ensure that "go SHORTCUT" switches to the correct drive on
  Windows when called in a subsystem:window environment (via the /D
  switch).
- Drop the '-o' option added by the DQSD go.xml search. This means
  that openning the given path in the _shell_ is now the default, as
  it is for command line usage.

### v0.8.1:
- Remove a debugging statement in 0.8.0 that caused "go SHORTCUT"
  to fail from Dave's Quick Search Deskbar.
- Install go.py as 'go' in Linux, which executable bit set. Before
  this, getting go going was a real pain. It still is somewhat.

### v0.8.0:
- Improve Windows integration: errors are now shown in dialogs rather
  than lost on the non-existant console.
- Improve DQSD integration. The default action is not to open a shell
  to the stated directory. "go -o" can be used, as on the command
  line, to open a directory in Explorer.
- Fix bug introduced in 0.7.0 whereby using go's innocuous options
  (-h, -V) could result in a directory change from the last "go"
  call.
- Add explicit "-c" option for the default "change directories"
  action.
- Improve shortcut listing output.

### v0.7.0:
- Add an optional argument when listing (-l|--list) to be a pattern
  for existing shortcuts, e.g.:
      go -l foo  # lists all shortcuts with foo in them
- Add DQSD (Dave's Quick Search Deskbar) integration. After
  installation and a re-start of DQSD you should be able to jump to
  directory shortcuts via "go SHORTCUT[/SUBPATH]" in DQSD.

### v0.6.3:
- first public release

