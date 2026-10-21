@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_execution_symmetry_evidence %*
exit /b %ERRORLEVEL%
