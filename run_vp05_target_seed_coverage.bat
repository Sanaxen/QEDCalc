@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_target_seed_coverage %*
exit /b %ERRORLEVEL%
