@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_physical_target_column_audit %*
exit /b %ERRORLEVEL%
