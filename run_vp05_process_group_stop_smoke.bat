@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_process_group_stop_smoke %*
exit /b %ERRORLEVEL%
