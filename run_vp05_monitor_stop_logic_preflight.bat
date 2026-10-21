@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_monitor_stop_logic_preflight %*
exit /b %ERRORLEVEL%
