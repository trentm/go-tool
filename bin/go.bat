@echo off
rem Windows shell driver for 'go' (http://code.google.com/p/go-tool/).
set GO_SHELL_SCRIPT=%TEMP%\__tmp_go.bat
call python -m go %1 %2 %3 %4 %5 %6 %7 %8 %9
if exist %GO_SHELL_SCRIPT% call %GO_SHELL_SCRIPT%
set GO_SHELL_SCRIPT=
