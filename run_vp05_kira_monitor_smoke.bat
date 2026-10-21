@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_kira_monitor_smoke %*
exit /b %ERRORLEVEL%
