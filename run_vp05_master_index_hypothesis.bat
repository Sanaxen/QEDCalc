@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_master_index_hypothesis %*
exit /b %ERRORLEVEL%
