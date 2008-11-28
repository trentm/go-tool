
# Some code from the old setup.py for installing DQSD support.

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

