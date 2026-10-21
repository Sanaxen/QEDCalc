@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_experiment_inventory %*
exit /b %ERRORLEVEL%
