@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kira_full_stage_specific_validation %*
exit /b %ERRORLEVEL%
