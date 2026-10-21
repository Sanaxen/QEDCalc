@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
 echo Usage: %~nx0 PATH_TO_pyred_weight.py [PATH_TO_EXPECTED_ALIAS_JSON]
 echo External GPL codec is not shipped with QEDCalc.
 exit /b 2
)
if not exist "%~1" (
 echo ERROR: Codec path does not exist: %~1
 exit /b 2
)
if "%~2"=="" (
 python -m examples.three_loop_sector203_target_codec_alias_audit --codec-file "%~1"
) else (
 python -m examples.three_loop_sector203_target_codec_alias_audit --codec-file "%~1" --expect "%~2"
)
exit /b %ERRORLEVEL%
