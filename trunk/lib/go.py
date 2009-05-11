#!/usr/bin/env python
# Copyright (c) 2002-2008 ActiveState Software.
# License: MIT License.
# Author: Trent Mick (trentm at google's mail thing)

"""
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
    "D:\\trentm\\main\\Apps\\Komodo-devel", then
        C:\\> go ko
        D:\\trentm\\main\\Apps\\Komodo-devel>
    and
        C:\\> go ko/test
        D:\\trentm\\main\\Apps\\Komodo-devel\\test>

    As well, you can always use some standard shortcuts, such as '~'
    (home) and '...' (up two dirs).

    See <http://code.google.com/p/go-tool/> for more information.
"""
# Dev Notes:
# - Shortcuts are stored in an XML file in your AppData folder.
#   On Windows this is typically:
#     <AppDataDir>\TrentMick\go\shortcuts.xml
#   On Linux (or other UN*X systems) this is typically:
#     ~/.go/shortcuts.xml

__version_info__ = (1, 2, 1)
__version__ = '.'.join(map(str, __version_info__))

import os
from os.path import splitext, expanduser, join, exists
import sys
import getopt
import re
import pprint
import codecs
import xml.dom.minidom



#---- exceptions

class GoError(Exception):
    pass

class InternalGoError(GoError):
    def __str__(self):
        return GoError.__str__(self) + """

* * * * * * * * * * * * * * * * * * * * * * * * * * * *
* Please log a bug at                                 *
*    http://code.google.com/p/go-tool/issues/list     *
* to report this error. Thanks!                       *
* -- Trent                                            *
* * * * * * * * * * * * * * * * * * * * * * * * * * * *"""



#---- globals

_envvar = "GO_SHELL_SCRIPT"

# On Windows, "console" or "windows" controls how some things behave.
_subsystem = "console"
if sys.platform.startswith("win") and\
   os.path.splitext(sys.executable)[0][-1] == 'w':
    _subsystem = "windows"
    
    
_gDriverFromShell = {
    "cmd": """\
@echo off
rem Windows shell driver for 'go' (http://code.google.com/p/go-tool/).
set GO_SHELL_SCRIPT=%TEMP%\__tmp_go.bat
call python -m go %1 %2 %3 %4 %5 %6 %7 %8 %9
if exist %GO_SHELL_SCRIPT% call %GO_SHELL_SCRIPT%
set GO_SHELL_SCRIPT=""",
    "sh": """\
# Bash shell driver for 'go' (http://code.google.com/p/go-tool/).
function go {
    export GO_SHELL_SCRIPT=$HOME/.__tmp_go.sh
    python -m go $*
    if [ -f $GO_SHELL_SCRIPT ] ; then
        source $GO_SHELL_SCRIPT
    fi
    unset GO_SHELL_SCRIPT
}""",
}



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
            elif os.path.isdir(path):
                target = ""
                suffix = path
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
            #TODO: Might want to prettily shorten long names.
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


def _getShell():
    if sys.platform == "win32":
        #assert "cmd.exe" in os.environ["ComSpec"]
        return "cmd"
    elif "SHELL" in os.environ:
        shell_path = os.environ["SHELL"]
        if "/bash" in shell_path or "/sh" in shell_path:
            return "sh"
        elif "/tcsh" in shell_path or "/csh" in shell_path:
            return "csh"
    else:
        raise InternalGoError("couldn't determine your shell (SHELL=%r)"
                              % os.environ.get("SHELL"))

def setup():
    from os.path import normcase, normpath, join

    shell = _getShell()
    try:
        driver = _gDriverFromShell[shell]
    except KeyError:
        raise InternalGoError("don't know how to setup for your shell: %s"
                              % shell)

    # Knowing the user's HOME dir will help later.
    nhome = None
    if "HOME" in os.environ:
        nhome = _normpath(os.environ["HOME"])
    elif "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
        nhome = _normpath(
            os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"])

    print "* * *"


    if shell == "cmd":
        # Need a install candidate dir for "go.bat".
        nprefix = _normpath(sys.prefix)
        ncandidates = set()
        candidates = []
        for dir in os.environ["PATH"].split(os.path.pathsep):
            ndir = _normpath(dir)
            if ndir.startswith(nprefix):
                if ndir not in ncandidates:
                    ncandidates.add(ndir)
                    candidates.append(dir)
            elif nhome and ndir.startswith(nhome) \
                 and ndir[len(nhome)+1:].count(os.path.sep) < 2:
                if ndir not in ncandidates:
                    ncandidates.add(ndir)
                    candidates.append(dir)
        #print candidates

        print """\
It appears that `go' is not setup properly in your environment. Typing
`go' must end up calling `go.bat' somewhere on your PATH and *not* `go.py'
directly. This is how `go' can change the directory in your current shell.

You'll need a file "go.bat" with the following contents in a directory on
your PATH:

%s""" % _indent(driver)

        if candidates:
            print "\nCandidate directories are:\n"
            for i, dir in enumerate(candidates):
                print "  [%s] %s" % (i+1, dir)

            print
            answer = _query_custom_answers(
                "If you would like this script to create `go.bat' for you in\n"
                    "one of these directories, enter the number of that\n"
                    "directory. Otherwise, enter 'no' to not create `go.bat'.",
                [str(i+1) for i in range(len(candidates))] + ["&no"],
                default="no",
            )
            if answer == "no":
                pass
            else:
                dir = candidates[int(answer)-1]
                path = join(dir, "go.bat")
                print "\nCreating `%s'." % path
                print "You should now be able to run `go --help'."
                open(path, 'w').write(driver)
    elif shell == "sh":
        print """\
It appears that `go' is not setup properly in your environment. Typing
`go' must end up calling the Bash function `go' and *not* `go.py'
directly. This is how `go' can change the directory in your current shell.

You'll need to have the following function in your shell startup script
(e.g. `.bashrc' or `.profile'):

%s

To just play around in your current shell, simple cut and paste this
function.""" % _indent(driver)

        candidates = ["~/.bashrc", "~/.bash_profile", "~/.bash_login",
                      "~/.profile"]
        candidates = [c for c in candidates if exists(expanduser(c))]
        if candidates:
            q = """\
Would you like this script to append `function go' to one of the following
Bash initialization scripts? If so, enter the number of the listed file.
Otherwise, enter `no'."""
            for i, path in enumerate(candidates):
                q += "\n (%d) %s" % (i+1, path)
            answers = [str(i+1) for i in range(len(candidates))] + ["&no"]
            print
            answer = _query_custom_answers(q, answers, default="no")
            if answer == "no":
                pass
            else:
                path = candidates[int(answer)-1]
                xpath = expanduser(path)
                f = codecs.open(xpath, 'a', 'utf-8')
                try:
                    f.write('\n\n'+driver)
                finally:
                    f.close()
                print
                print "`function go' appended to `%s'." % path
                print "Run `source %s` to enable this for this shell." % path
                print "You should then be able to run `go --help'."
    else:
        print """\
It appears that `go' is not setup properly in your environment. Typing
`go' must end up calling the shell function `go' and *not* `go.py'
directly. This is how `go' can change the directory in your current shell.

The appropriate function for the *Bash* shell is this:

%s

If you know the appropriate translation for your shell (%s) I'd appreciate
your feedback on that so I can update this script. Please add an issue here:

    http://code.google.com/p/go-tool/issues/list

Thanks!""" % (_indent(_gDriverFromShell["sh"]), shell)

    print "* * *"


# Recipe: query_custom_answers (1.0)
def _query_custom_answers(question, answers, default=None):
    """Ask a question via raw_input() and return the chosen answer.
    
    @param question {str} Printed on stdout before querying the user.
    @param answers {list} A list of acceptable string answers. Particular
        answers can include '&' before one of its letters to allow a
        single letter to indicate that answer. E.g., ["&yes", "&no",
        "&quit"]. All answer strings should be lowercase.
    @param default {str, optional} A default answer. If no default is
        given, then the user must provide an answer. With a default,
        just hitting <Enter> is sufficient to choose. 
    """
    prompt_bits = []
    answer_from_valid_choice = {
        # <valid-choice>: <answer-without-&>
    }
    clean_answers = []
    for answer in answers:
        if '&' in answer and not answer.index('&') == len(answer)-1:
            head, tail = answer.split('&', 1)
            prompt_bits.append(head.lower()+tail.lower().capitalize())
            clean_answer = head+tail
            shortcut = tail[0].lower()
        else:
            prompt_bits.append(answer.lower())
            clean_answer = answer
            shortcut = None
        if default is not None and clean_answer.lower() == default.lower():
            prompt_bits[-1] += " (default)"
        answer_from_valid_choice[clean_answer.lower()] = clean_answer
        if shortcut:
            answer_from_valid_choice[shortcut] = clean_answer
        clean_answers.append(clean_answer.lower())

    # This is what it will look like:
    #   Frob nots the zids? [Yes (default), No, quit] _
    # Possible alternatives:
    #   Frob nots the zids -- Yes, No, quit? [y] _
    #   Frob nots the zids? [*Yes*, No, quit] _
    #   Frob nots the zids? [_Yes_, No, quit] _
    #   Frob nots the zids -- (y)es, (n)o, quit? [y] _
    prompt = " [%s] " % ", ".join(prompt_bits)
    leader = question + prompt
    if len(leader) + max(len(c) for c in answer_from_valid_choice) > 78:
        leader = question + '\n' + prompt.lstrip()
    leader = leader.lstrip()

    valid_choices = answer_from_valid_choice.keys()
    admonishment = "*** Please respond with '%s' or '%s'. ***" \
                   % ("', '".join(clean_answers[:-1]), clean_answers[-1])

    while 1:
        sys.stdout.write(leader)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in answer_from_valid_choice:
            return answer_from_valid_choice[choice]
        else:
            sys.stdout.write("\n"+admonishment+"\n\n\n")



# Recipe: indent (0.2.1)
def _indent(s, width=4, skip_first_line=False):
    """_indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)


def _normpath(path):
    from os.path import normcase, normpath
    n = normcase(normpath(path))
    if n.endswith(os.path.sep):
        n = n[:-1]
    elif os.path.altsep and n.endswith(os.path.altsep):
        n = n[:-1]
    return n


#---- mainline

def main(argv):
    # Must write out a no-op shell script before any error can happen
    # otherwise the script from the previous run could result.
    try:
        shellScript = os.environ[_envvar]
    except KeyError:
        if _subsystem == "windows":
            pass # Don't complain about missing console setup.
        return setup()
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


