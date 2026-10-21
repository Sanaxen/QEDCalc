@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_kira_symmetry_execution_trace %*
exit /b %ERRORLEVEL%
