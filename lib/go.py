#!/usr/bin/env python
# Copyright (c) 2002-2005 ActiveState Corp.
# See LICENSE.txt for license details.
# Author:
#   Trent Mick (TrentM@ActiveState.com)
# Home:
#   http://trentm.com/projects/go/

"""
    Quick directory changing.

    Usage:
        go <shortcut>[/sub/dir/path]    # change directories
                                        # same as "go -c ..."
        go -c|-o|-a|-d|-s ...           # cd to, open, add, delete, set
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
    "D:\\trentm\\main\\Apps\\Komodo-devel", then
        C:\\> go ko
        D:\\trentm\\main\\Apps\\Komodo-devel>
    and
        C:\\> go ko/test
        D:\\trentm\\main\\Apps\\Komodo-devel\\test>

    As well, you can always use some standard shortcuts, such as '~'
    (home) and '...' (up two dirs).

    See <http://trentm.com/projects/go> for more information.
"""
# Dev Notes:
# - Shortcuts are stored in an XML file in your AppData folder.
#   On Windows this is typically:
#     <AppDataDir>\TrentMick\go\shortcuts.xml
#   On Linux (or other UN*X systems) this is typically:
#     ~/.go/shortcuts.xml

__version_info__ = (1, 0, 6)
__version__ = '.'.join(map(str, __version_info__))

import os
import sys
import getopt
import re
import pprint
import xml.dom.minidom



#---- exceptions

class GoError(Exception):
    pass


#---- globals

_envvar = "GO_SHELL_SCRIPT"

# On Windows, "console" or "windows" controls how some things behave.
_subsystem = "console"
if sys.platform.startswith("win") and\
   os.path.splitext(sys.executable)[0][-1] == 'w':
    _subsystem = "windows"
    


#---- public module interface

def getShortcutsFile():
    """Return the path to the shortcuts file."""
    fname = "shortcuts.xml"
    if sys.platform.startswith("win"):
        # Favour ~/.go if shortcuts.xml already exists there, otherwise
        # favour CSIDL_APPDATA/... if have win32com to *find* that dir.
        dname = os.path.expanduser("~/.go")
        shortcutsFile = os.path.join(dname, fname)
        if not os.path.isfile(shortcutsFile):
            try:
                from win32com.shell import shellcon, shell
                dname = os.path.join(
                    shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0),
                    "TrentMick", "Go")
                shortcutsFile = os.path.join(dname, fname)
            except ImportError:
                pass
    else:
        dname = os.path.expanduser("~/.go")
        shortcutsFile = os.path.join(dname, fname)
    return shortcutsFile


def getDefaultShortcuts():
    """Return the dictionary of default shortcuts."""
    if sys.platform == "win32" and sys.version.startswith("2.3."):
        import warnings
        warnings.filterwarnings("ignore", module="fcntl", lineno=7)
    import tempfile
    shortcuts = {
        '.': os.curdir,
        '..': os.pardir,
        '...': os.path.join(os.pardir, os.pardir),
        'tmp': tempfile.gettempdir(),
    }
    try:
        shortcuts['~'] = os.environ['HOME']
    except KeyError:
        pass
    return shortcuts


def setShortcut(name, value):
    """Add the given shortcut mapping to the XML database.
    
        <shortcuts version="...">
            <shortcut name="..." value="..."/>
        </shortcuts>

    A value of None deletes the named shortcut.
    """
    shortcutsXml = getShortcutsFile()
    if os.path.isfile(shortcutsXml):
        dom = xml.dom.minidom.parse(shortcutsXml)
    else:
        dom = xml.dom.minidom.parseString(
                    '<shortcuts version="1.0"></shortcuts>')

    shortcuts = dom.getElementsByTagName("shortcuts")[0]
    for s in shortcuts.getElementsByTagName("shortcut"):
        if s.getAttribute("name") == name:
            if value:
                s.setAttribute("value", value)
            else:
                shortcuts.removeChild(s)
            break
    else:
        if value:
            s = dom.createElement("shortcut")
            s.setAttribute("name", name)
            s.setAttribute("value", value)
            shortcuts.appendChild(s)
        else:
            raise GoError("shortcut '%s' does not exist" % name)

    if not os.path.isdir(os.path.dirname(shortcutsXml)):
        os.makedirs(os.path.dirname(shortcutsXml))
    fout = open(shortcutsXml, 'w')
    fout.write(dom.toxml())
    fout.close()


def getShortcuts():
    """Return the shortcut dictionary."""
    shortcuts = getDefaultShortcuts()

    shortcutsXml = getShortcutsFile()
    if os.path.isfile(shortcutsXml):
        dom = xml.dom.minidom.parse(shortcutsXml)
        shortcutsNode = dom.getElementsByTagName("shortcuts")[0]
        for shortcutNode in shortcutsNode.getElementsByTagName("shortcut"):
            name = shortcutNode.getAttribute("name")
            value = shortcutNode.getAttribute("value")
            shortcuts[name] = value

    return shortcuts


def resolvePath(path):
    """Return a dir for the given <shortcut>[/<subpath>].

    Raises a GoError if the shortcut does not exist.
    """
    shortcuts = getShortcuts()

    if path:
        tagend = path.find('/')
        if tagend == -1:
            tagend = path.find('\\')
        if tagend == -1:
            tag, suffix = path, None
        else:
            tag, suffix = path[:tagend], path[tagend+1:]
        try:
            target = shortcuts[tag]
        except KeyError:
            # Bash will expand ~ (used as a shortcut) into the user's
            # actual home directory. We still want to support '~' as a
            # shortcut in Bash so try to determine if it is likely that
            # the user typed it and act accordingly.
            home = os.path.expanduser('~')
            if path.startswith(home):
                tag, suffix = '~', path[len(home)+1:]
                target = shortcuts[tag]
            else:
                raise
        if suffix:
            target = os.path.join(target, os.path.normpath(suffix))
    else:
        raise GoError("no path was given")

    return target
    

def generateShellScript(scriptName, path=None):
    """Generate a shell script with the given name to change to the
    given shortcut path.

    "scriptName" is the path to the script the create.
    "path" is the shortcut path, i.e. <shortcut>[/<subpath>]. If path is
        None (the default) a no-op script is written.
    """
    shortcuts = getShortcuts()
    if path is None:
        target = None
    else:
        target = resolvePath(path)

    if sys.platform.startswith("win"):
        fbat = open(scriptName, 'w')
        fbat.write('@echo off\n')
        if target:
            drive, tail = os.path.splitdrive(target)
            fbat.write('@echo off\n')
            if drive:
                fbat.write('call %s\n' % drive)
            fbat.write('call cd "%s"\n' % target)
            fbat.write('title "%s"\n' % target)
        fbat.close()
    else:
        fsh = open(scriptName, 'w')
        fsh.write('#!/bin/sh\n')
        if target:
            fsh.write('cd "%s"\n' % target)
        fsh.close()


def printShortcuts(shortcuts, subheader=None):
    # Organize the shortcuts into groups.
    defaults = [re.escape(s) for s in getDefaultShortcuts().keys()]
    groupMap = { # mapping of group regex to group order and title
        "^(%s)$" % '|'.join(defaults): (0, "Default shortcuts"),
        None: (1, "Custom shortcuts"),
    }
    grouped = {
        # <group title>: [<member shortcuts>...]
    }
    for shortcut in shortcuts:
        for pattern, (order, title) in groupMap.items():
            if pattern and re.search(pattern, shortcut):
                if title in grouped:
                    grouped[title].append(shortcut)
                else:
                    grouped[title] = [shortcut]
                break
        else:
            title = "Custom shortcuts"
            if title in grouped:
                grouped[title].append(shortcut)
            else:
                grouped[title] = [shortcut]
    for memberList in grouped.values(): memberList.sort()
    groups = []
    titles = groupMap.values()
    titles.sort()

    # Construct the table.
    table = ""
    header = "Go Shortcuts"
    if subheader:
        header += ": " + subheader
    table += ' '*20 + header + '\n'
    table += ' '*20 + '='*len(header) + '\n'
    for order, title in titles:
        if title not in grouped: continue
        table += '\n' + title + ":\n"
        for shortcut in grouped[title]:
            dir = shortcuts[shortcut]
            #XXX Might want to prettily shorten long names.
            #if len(dir) > 53:
            #    dir = dir[:50] + "..."
            table += "  %-20s  %s\n" % (shortcut, dir)

    # Display the table.
    if _subsystem == "windows":
        import win32ui
        import win32con
        win32ui.MessageBox(table, "Go Shortcuts",
                           win32con.MB_OK | win32con.MB_ICONINFORMATION)
        
    else:
        sys.stdout.write(table)


def error(msg):
    if _subsystem == "console":
        sys.stderr.write("go: error: %s\n" % msg)
    elif _subsystem == "windows" and sys.platform.startswith("win"):
        import win32ui
        import win32con
        win32ui.MessageBox(msg, "Go Error",
                           win32con.MB_OK | win32con.MB_ICONERROR)
    else:
        raise ValueError("internal error: unrecognized subsystem, '%s', and "
                         "platform, '%s'." % (_subsystem, sys.platform))


#---- mainline

def main(argv):
    # Must write out a no-op shell script before any error can happen
    # otherwise the script from the previous run could result.
    try:
        shellScript = os.environ[_envvar]
    except KeyError:
        if _subsystem == "windows":
            pass # Don't complain about missing console setup.
        elif sys.platform.startswith('win'):
            sys.stderr.write("""* * *
It appears that 'go' is not setup properly in your environment. Typing
'go' should end up calling go.bat somewhere on your PATH and *not* go.py
directly. Both go.bat and go.bat should be installed automatically by
the setup.py script.
* * *
""")
            return 1
        else:
            sys.stderr.write(r"""* * *
It appears that 'go' is not setup properly in your environment.  If you
are using the Bash shell you should have the following function in your
environment:

    function go {
        export GO_SHELL_SCRIPT=$HOME/.__tmp_go.sh
        python -m go $*
        if [ -f $GO_SHELL_SCRIPT ] ; then
            source $GO_SHELL_SCRIPT
        fi
    }

You should add the above function to your ~/.bashrc file or just cut and
paste the function into your current shell.
* * *
""")
            return 1
    else:
        generateShellScript(shellScript) # no-op, overwrite old one

    # Parse options
    try:
        shortopts = "hVcsadl"
        longopts = ['help', 'version', 'cd', 'set', 'add-current',
                    'delete', 'list']
        if sys.platform.startswith("win"):
            shortopts += "o"
            longopts.append("open")
        optlist, args = getopt.getopt(argv[1:], shortopts, longopts)
    except getopt.GetoptError, ex:
        msg = ex.msg
        if ex.opt in ('d', 'dump'):
            msg += ": old -d|--dump option is now -l|--list"
        sys.stderr.write("go: error: %s.\n" % msg)
        sys.stderr.write("See 'go --help'.\n")
        return 1
    action = "cd"
    for opt, optarg in optlist:
        if opt in ('-h', '--help'):
            sys.stdout.write(__doc__)
            return 0
        elif opt in ('-V', '--version'):
            sys.stdout.write("go %s\n" % __version__)
            return 0
        elif opt in ('-c', '--cd'):
            action = "cd"
        elif opt in ('-s', '--set'):
            action = "set"
        elif opt in ('-a', '--add-current'):
            action = "add"
        elif opt in ('-d', '--delete'):
            action = "delete"
        elif opt in ('-l', '--list'):
            action = "list"
        elif opt in ("-o", "--open"):
            action = "open"

    # Parse arguments and do specified action.
    if action == "add":
        if len(args) != 1:
            error("Incorrect number of arguments. argv: %s" % argv)
            return 1
        name, value = args[0], os.getcwd()
        try:
            setShortcut(name, value)
        except GoError, ex:
            error(str(ex))
            return 1

    elif action == "delete":
        if len(args) != 1:
            error("Incorrect number of arguments. argv: %s" % argv)
            return 1
        name, value = args[0], None
        try:
            setShortcut(name, value)
        except GoError, ex:
            error(str(ex))
            return 1

    elif action == "set":
        if len(args) != 2:
            error("Incorrect number of arguments. argv: %s" % argv)
            return 1
        name, value = args
        try:
            setShortcut(name, value)
        except GoError, ex:
            error(str(ex))
            return 1

    elif action == "cd":
        if len(args) != 1:
            error("Incorrect number of arguments. argv: %s" % argv)
            #error("Usage: go [options...] shortcut[/subpath]")
            return 1
        path = args[0]
        if _subsystem == "console":
            try:
                generateShellScript(shellScript, path)
            except KeyError, ex:
                error("Unrecognized shortcut: '%s'" % str(ex))
                return 1
            except GoError, ex:
                error(str(ex))
                return 1
        elif _subsystem == "windows" and sys.platform.startswith("win"):
            try:
                dir = resolvePath(path)
            except GoError, ex:
                error("Error resolving '%s': %s" % (path, ex))
                return 1
            try:
                comspec = os.environ["COMSPEC"]
            except KeyError:
                error("Could not determine shell. No COMSPEC environment "
                      "variable.")
                return 1

            argv = [comspec, "/k",      # Does command.com support '/k'?
                    "cd", "/D", '"%s"' % dir]
            if os.path.basename(comspec).lower() == "cmd.exe":
                argv += ["&&", "title", '%s' % dir]
            os.spawnv(os.P_NOWAIT, comspec, argv)
            
        else:
            error("Internal error: subsystem is 'windows' and platform is "
                  "not win32")
            return 1

    elif action == "list":
        if len(args) == 0:
            printShortcuts(getShortcuts())
        elif len(args) == 1:
            pattern = args[0].lower()
            shortcuts = getShortcuts()
            s = {}
            for name, value in shortcuts.items():
                if name.lower().find(pattern) != -1:
                    s[name] = value
            printShortcuts(s, "Matching '%s'" % pattern)
        else:
            error("Incorrect number of arguments. argv: %s" % argv)
            return 1

    elif action == "open" and sys.platform.startswith("win"):
        if len(args) != 1:
            error("Incorrect number of arguments. argv: %s" % argv)
            return 1
        path = args[0]

        try:
            dir = resolvePath(path)
        except GoError, ex:
            error("Error resolving '%s': %s" % (path, ex))
            return 1

        import win32api
        try:
            explorerExe, offset = win32api.SearchPath(None, "explorer.exe")
        except win32api.error, ex:
            error("Could not find 'explorer.exe': %s" % ex)
            return 1

        os.spawnv(os.P_NOWAIT, explorerExe, [explorerExe, '/E,"%s"' % dir])

    else:
        error("Internal Error: unknown action: '%s'\n")
        return 1
        

if __name__ == "__main__":
    if _subsystem == "windows":
        try:
            retval = main(sys.argv)
        except:
            import traceback
            tb = ''.join(traceback.format_exception(*sys.exc_info()))
            error(tb)
    else:
        retval = main(sys.argv)
    sys.exit(retval)


