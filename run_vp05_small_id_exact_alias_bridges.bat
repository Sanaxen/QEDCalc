@echo off
setlocal
cd /d "%~dp0"
set "CODEC_FILE=%~1"
if not defined CODEC_FILE set "CODEC_FILE=output\tools\pyred_weight.py"
if not exist "%CODEC_FILE%" (
 echo ERROR: Codec file not found: "%CODEC_FILE%"
 exit /b 2
)
python -m examples.three_loop_sector203_small_id_exact_alias_bridges --codec-file "%CODEC_FILE%"
exit /b %ERRORLEVEL%
