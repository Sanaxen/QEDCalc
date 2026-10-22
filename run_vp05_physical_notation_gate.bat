@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_physical_notation_gate
exit /b %ERRORLEVEL%
