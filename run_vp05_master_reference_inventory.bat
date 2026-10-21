@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_master_reference_inventory %*
exit /b %ERRORLEVEL%
