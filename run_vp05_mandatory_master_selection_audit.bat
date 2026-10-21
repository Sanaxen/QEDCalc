@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_mandatory_master_selection_audit %*
exit /b %ERRORLEVEL%
