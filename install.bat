@echo off
setlocal
ECHO [INSTALL] Running unified environment install...
ECHO.
where python >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
    python install_agent_env.py %*
    exit /b %ERRORLEVEL%
)

where py >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
    py install_agent_env.py %*
    exit /b %ERRORLEVEL%
)

ECHO Python is required to run install_agent_env.py
exit /b 1
