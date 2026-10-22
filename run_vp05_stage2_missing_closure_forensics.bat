@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_missing_closure_forensics
exit /b %ERRORLEVEL%
