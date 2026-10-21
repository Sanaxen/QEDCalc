@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
 echo Usage: %~nx0 PATH_TO_pyred_weight.py
 exit /b 2
)
python -m examples.three_loop_sector203_small_weight_diagnostic --codec-file "%~1"
exit /b %ERRORLEVEL%
