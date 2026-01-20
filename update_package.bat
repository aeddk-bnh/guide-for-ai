@echo off
ECHO ==========================================
ECHO      AGENT PACKAGE UPDATE UTILITY
ECHO ==========================================

:: 1. Copy latest files
CALL prepare_package.bat

:: 2. Bump Version & Publish
cd npm_dist

ECHO.
ECHO [ACTION] Bumping version (Patch)...
call npm version patch --no-git-tag-version

ECHO.
ECHO [ACTION] Publishing to NPM...
call npm publish

cd ..

ECHO.
ECHO ==========================================
ECHO [SUCCESS] Update Complete!
ECHO You can now update on other machines using:
ECHO     npx <your-package-name>@latest
ECHO ==========================================
PAUSE
