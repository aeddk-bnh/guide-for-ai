@echo off
ECHO [UPDATE] Pulling latest changes...
git pull origin main

ECHO.
ECHO [INSTALL] Re-applying configuration...
call install.bat
