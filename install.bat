@echo off
ECHO [INSTALL] Setting up Agent Environment...
ECHO.
python setup_agent_env.py
IF %ERRORLEVEL% NEQ 0 (
   py setup_agent_env.py
)
PAUSE
