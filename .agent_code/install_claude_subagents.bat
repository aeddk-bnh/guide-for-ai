@echo off
setlocal EnableDelayedExpansion

:: Initialize default target
set "TARGET=claude-agents"

:: Parse command line arguments
:parse_args
if "%~1"=="" goto args_end
if /i "%~1"=="-t" (
    set "TARGET=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="/?" (
    call :show_help
    goto :eof
)
if /i "%~1"=="-h" (
    call :show_help
    goto :eof
)
echo Error: Unknown argument "%~1"
call :show_help
goto :eof

:args_end

:: Determine source and target directories based on user choice
if /i "!TARGET!"=="claude-agents" (
    set "SOURCE_DIR=%~dp0subagents"
    set "TARGET_DIR=%USERPROFILE%\.claude\agents"
    set "PRODUCT_NAME=Claude Code"
    set "ITEM_TYPE=agents"
    goto :execute_install
)
if /i "!TARGET!"=="opencode-agents" (
    set "SOURCE_DIR=%~dp0subagents"
    set "TARGET_DIR=%USERPROFILE%\.config\opencode\agents"
    set "PRODUCT_NAME=OpenCode"
    set "ITEM_TYPE=agents"
    goto :execute_install
)
if /i "!TARGET!"=="claude-skills" (
    set "SOURCE_DIR=%~dp0skills"
    set "TARGET_DIR=%USERPROFILE%\.claude\skills"
    set "PRODUCT_NAME=Claude Code"
    set "ITEM_TYPE=skills"
    goto :execute_install
)
if /i "!TARGET!"=="opencode-skills" (
    set "SOURCE_DIR=%~dp0skills"
    set "TARGET_DIR=%USERPROFILE%\.config\opencode\skills"
    set "PRODUCT_NAME=OpenCode"
    set "ITEM_TYPE=skills"
    goto :execute_install
)
if /i "!TARGET!"=="antigravity-agents" (
    set "SOURCE_DIR=%~dp0subagents"
    set "TARGET_DIR=%USERPROFILE%\.gemini\antigravity\agents"
    set "PRODUCT_NAME=Antigravity"
    set "ITEM_TYPE=agents"
    goto :execute_install
)
if /i "!TARGET!"=="antigravity-skills" (
    set "SOURCE_DIR=%~dp0skills"
    set "TARGET_DIR=%USERPROFILE%\.gemini\antigravity\skills"
    set "PRODUCT_NAME=Antigravity"
    set "ITEM_TYPE=skills"
    goto :execute_install
)

:: If we reach here, the target was invalid
echo Error: Invalid target '!TARGET!'. Please specify 'claude-agents', 'opencode-agents', 'claude-skills', 'opencode-skills', 'antigravity-agents' or 'antigravity-skills'.
call :show_help
goto :eof

:execute_install

echo.
echo Starting !PRODUCT_NAME! !ITEM_TYPE! Installation for Windows...
echo Source directory: !SOURCE_DIR!
echo Target directory: !TARGET_DIR!
echo.

:: Check if source directory exists
if not exist "!SOURCE_DIR!" (
    echo Error: Source directory '!SOURCE_DIR!' not found. Please ensure it exists.
    goto :eof
)

:: Create target directory if it doesn't exist
if not exist "!TARGET_DIR!" (
    echo Creating target directory: !TARGET_DIR!
    mkdir "!TARGET_DIR!"
    if errorlevel 1 (
        echo Error: Failed to create target directory '!TARGET_DIR!'.
        goto :eof
    )
)

:: For skills, we need to copy the entire subdirectory structure
if /i "!ITEM_TYPE!"=="skills" (
    echo Copying skill directories from '!SOURCE_DIR!' to '!TARGET_DIR!'...
    robocopy "!SOURCE_DIR!" "!TARGET_DIR!" /E /R:0 /NFL /NDL /NP
    if errorlevel 8 (
        echo Error: robocopy reported a fatal error exit code 8 or higher.
        goto :eof
    )
    goto :post_process
)

:: For agents, copy individual .md files
:: Check if there are any .md files in the target that would be overwritten
set "OVERWRITE_NEEDED=false"
for %%f in ("!SOURCE_DIR!\*.md") do (
    if exist "!TARGET_DIR!\%%~nxf" (
        set "OVERWRITE_NEEDED=true"
        REM The loop continues, but we only need to know if ANY file existed.
    )
)

:: Check the flag set by the FOR loop
if "!OVERWRITE_NEEDED!"=="true" (
    echo Warning: Some !ITEM_TYPE! files already exist in the target directory.
    set /p CHOICE="Do you want to overwrite existing files? (Y/N): "
    if /i not "!CHOICE!"=="Y" (
        echo Installation aborted by user.
        goto :eof
    )
)

echo Copying !ITEM_TYPE! files from '!SOURCE_DIR!' to '!TARGET_DIR%'...
xcopy "!SOURCE_DIR!\*.md" "!TARGET_DIR!\" /Y /R /Q /F
if errorlevel 1 (
    echo Error: Failed to copy !ITEM_TYPE! files.
    goto :eof
)

:post_process

:: Post-processing for OpenCode Agents
if /i "!TARGET!"=="opencode-agents" (
    echo.
    echo Modifying agent configurations for OpenCode format...
    
    REM Check if Python is available
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Warning: Python is not found. Cannot automatically convert agent configuration format.
        echo Please ensure you have Python installed to fix the formatting in '!TARGET_DIR!'.
    ) else (
        REM Run python script to fix formatting in target directory
        python "%~dp0manage_agent_config.py" fix-opencode "!TARGET_DIR!"
    )
)

:: Post-processing for Antigravity Skills
if /i "!TARGET!"=="antigravity-skills" (
    echo.
    echo Restructuring skills for Antigravity format...
    
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Warning: Python is not found. Cannot automatically restructure skills.
    ) else (
        python "%~dp0manage_agent_config.py" fix-antigravity-skills "!TARGET_DIR!"
    )
)

:: Post-processing for continuous-learning-v2 skill
if exist "!TARGET_DIR!\\continuous-learning-v2" (
    echo.
    echo Configuring continuous-learning-v2 skill...
    
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Warning: Python is not found. Cannot automatically configure the skill.
    ) else (
        python "%~dp0manage_agent_config.py" fix-skill-paths "!TARGET_DIR!\\continuous-learning-v2" "!TARGET_DIR!\\.."
    )
)

:installation_complete
echo.
echo Installation complete!
echo You may need to restart your !PRODUCT_NAME! session for the new !ITEM_TYPE! to load.
echo.

endlocal
goto :eof

:: Function to display help
:show_help
echo Usage: %~nx0 [-t target]
echo   -t target : Install target (claude/opencode/antigravity-agents/skills). Default is claude-agents.
echo   -h, /?    : Show this help message.
goto :eof
