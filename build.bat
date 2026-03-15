@echo off
setlocal

set "PYTHON_EXE=py"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

set "LANG_TARGET=%~1"
if "%LANG_TARGET%"=="" set "LANG_TARGET=all"

set "CACHE_ARG="
if /I "%~2"=="refreshcache" set "CACHE_ARG=--refresh-icon-cache"

%PYTHON_EXE% scripts\build.py --lang %LANG_TARGET% %CACHE_ARG%
exit /b %ERRORLEVEL%
