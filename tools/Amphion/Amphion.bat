@REM call this bat file to run cli with environment(embedded python)
@echo off

cd /d "%~dp0"
@REM add ..\runtime\Scripts to PATH
set PATH=%~dp0..\runtime\Scripts;%PATH%
..\runtime\python como_cli.py %*
exit /b %ERRORLEVEL%