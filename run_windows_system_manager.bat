@echo off
setlocal EnableDelayedExpansion

title Windows System Manager Launcher

:: Self-elevate to administrative privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %ERRORLEVEL% NEQ 0 (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto GotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:GotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

cls
echo ===============================================
echo   Windows System Manager Launcher
echo ===============================================
echo.
echo WARNING: This application is designed exclusively for Windows.
echo It will not work on any other operating system.
echo.

echo [1/4] Checking system requirements...

REM Check if running on Windows
ver | find "Windows" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: This application requires Windows operating system.
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

REM Check Python version (needs 3.7+)
for /f "tokens=2" %%V in ('python -c "import sys; print(sys.version.split()[0])"') do set pyver=%%V
for /f "tokens=1,2 delims=." %%a in ("!pyver!") do (
    set major=%%a
    set minor=%%b
)
if !major! LSS 3 (
    echo ERROR: Python version 3.7 or higher is required.
    echo Current version: !pyver!
    echo Please upgrade your Python installation.
    echo.
    pause
    exit /b 1
)
if !major! EQU 3 (
    if !minor! LSS 7 (
        echo ERROR: Python version 3.7 or higher is required.
        echo Current version: !pyver!
        echo Please upgrade your Python installation.
        echo.
        pause
        exit /b 1
    )
)

echo [2/4] Checking dependencies...

REM Install dependencies if needed
set missing_deps=0
python -c "import PyQt5" >nul 2>nul || set missing_deps=1
python -c "import psutil" >nul 2>nul || set missing_deps=1
python -c "import win32api" >nul 2>nul || set missing_deps=1

if !missing_deps! EQU 1 (
    echo [3/4] Installing required dependencies...
    
    REM First check pip
    python -m pip --version >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: pip is not installed or not working.
        echo Please reinstall Python with pip included.
        echo.
        pause
        exit /b 1
    )
    
    REM Install or update pip
    echo Upgrading pip...
    python -m pip install --upgrade pip
    
    REM Install required packages
    echo Installing PyQt5, psutil, and pywin32...
    python -m pip install PyQt5 psutil pywin32
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Please refer to INSTALL.txt for manual installation instructions.
        echo.
        pause
        exit /b 1
    )
    
    REM Verify installation
    set verify_fail=0
    python -c "import PyQt5" >nul 2>nul || set verify_fail=1
    python -c "import psutil" >nul 2>nul || set verify_fail=1
    python -c "import win32api" >nul 2>nul || set verify_fail=1
    
    if !verify_fail! EQU 1 (
        echo.
        echo ERROR: Failed to verify dependencies after installation.
        echo Please refer to INSTALL.txt for troubleshooting.
        echo.
        pause
        exit /b 1
    )
) else (
    echo All dependencies are already installed.
)

echo [4/4] Launching Windows System Manager...
echo.

REM Run the application with error handling
python main.py
set app_exit=%ERRORLEVEL%

if !app_exit! NEQ 0 (
    echo.
    echo ERROR: The application exited with code !app_exit!
    
    REM Provide more specific error messages
    if !app_exit! EQU 9009 (
        echo Python could not be found or executed.
    ) else if !app_exit! GEQ 1 (
        if !app_exit! LSS 10 (
            echo There was a problem initializing the application.
        ) else (
            echo There was a runtime error in the application.
        )
    )
    
    echo.
    echo Please try the following:
    echo 1. Make sure all required dependencies are installed
    echo 2. Run the application with administrator privileges
    echo 3. Check INSTALL.txt for detailed troubleshooting steps
    echo.
    echo Technical details: Error code !app_exit!
    echo.
    pause
)

exit /b !app_exit!