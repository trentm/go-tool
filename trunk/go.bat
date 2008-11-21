@echo off
rem Copyright (c) 2002-2003 ActiveState Corp.
rem Author: Trent Mick (TrentM@ActiveState.com)
set GO_SHELL_SCRIPT=%TEMP%\__tmp_go.bat
call go.py %1 %2 %3 %4 %5 %6 %7 %8 %9
if exist %GO_SHELL_SCRIPT% call %GO_SHELL_SCRIPT%
set GO_SHELL_SCRIPT=
