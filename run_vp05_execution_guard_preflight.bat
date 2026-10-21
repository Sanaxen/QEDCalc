@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_execution_guard_preflight %*
exit /b %ERRORLEVEL%
