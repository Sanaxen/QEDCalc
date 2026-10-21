@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_group_remaining %*
exit /b %ERRORLEVEL%
