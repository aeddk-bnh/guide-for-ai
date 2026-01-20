@echo off
ECHO [BUILD] Preparing NPM Package...

:: Ensure we are in the script directory
pushd "%~dp0"

:: Source is the .agent_code SUBDIRECTORY inside the current directory
SET SRC=.agent_code
SET DEST=npm_dist\assets

IF EXIST "%DEST%" (
    RMDIR /S /Q "%DEST%"
)

MKDIR "%DEST%"
MKDIR "%DEST%\core"
MKDIR "%DEST%\workflows"
MKDIR "%DEST%\skills"

ECHO Copying from %SRC% to %DEST%...

ROBOCOPY "%SRC%\core" "%DEST%\core" *.md /E /NFL /NDL /NJH /NJS
ROBOCOPY "%SRC%\workflows" "%DEST%\workflows" *.md /E /NFL /NDL /NJH /NJS
ROBOCOPY "%SRC%\skills" "%DEST%\skills" *.md /E /NFL /NDL /NJH /NJS

ECHO [BUILD] Assets copied. Package is ready in 'npm_dist'.
popd
