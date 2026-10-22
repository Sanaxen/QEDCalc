@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_unresolved_alias_diagnosis
exit /b %ERRORLEVEL%
