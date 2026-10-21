@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_wsl_resource_preflight %*
exit /b %ERRORLEVEL%
