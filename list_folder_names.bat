@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
set /p FOLDER=Paste the folder path and press Enter: 
if "!FOLDER!"=="" (
  echo No path given.
  pause
  exit /b 1
)

rem Remove quotes if the path was pasted with them
set FOLDER=!FOLDER:"=!

if not exist "!FOLDER!\" (
  echo That path is not a folder:
  echo !FOLDER!
  pause
  exit /b 1
)

echo.
echo Listing all folders under:
echo !FOLDER!
echo Please wait...
echo.

dir /ad /s /b "!FOLDER!" > "%~dp0folder_names.txt"

echo Done.
echo Full list saved here:
echo %~dp0folder_names.txt
echo.
pause
