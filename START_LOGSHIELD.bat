@echo off
title LogShield
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app.py
) else (
  python app.py
)
if errorlevel 1 (
 echo.
 echo Could not start LogShield. Please install Python 3 from https://www.python.org/downloads/
 echo During installation, tick "Add Python to PATH".
 pause
)
