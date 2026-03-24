@echo off
ECHO [INSTALL] Running unified environment install...
ECHO.
python install_agent_env.py %*
IF %ERRORLEVEL% NEQ 0 (
   py install_agent_env.py %*
)
