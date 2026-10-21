@echo off
setlocal
cd /d "%~dp0"
wsl -- python3 -m examples.three_loop_sector203_full_stage_guarded_run %*
exit /b %ERRORLEVEL%
