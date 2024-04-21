@REM call this bat file to run cli with environment(embedded python)
@echo off

cd /d "%~dp0"
"..\runtime\python" cli.py %*
exit /b %ERRORLEVEL%