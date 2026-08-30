@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "PYTHONPATH=%CD%"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
set "OUT=test_results\v051_crossed_%STAMP%"
mkdir "%OUT%" >nul 2>&1
set "MASTER=%OUT%\validation.log"
set "FAIL=0"

echo QEDCalc v0.51 crossed validation > "%MASTER%"
echo Started: %DATE% %TIME%>> "%MASTER%"
echo.>> "%MASTER%"

echo [1/8] Phase 26...
"%PY%" examples\phase26_crossed_independent_analytic_trial.py > "%OUT%\phase26.log" 2>&1
if errorlevel 1 set "FAIL=1"
type "%OUT%\phase26.log" >> "%MASTER%"
if "!FAIL!"=="1" goto :finish

set N=1
for %%F in (
  tests\test_v051_crossed_independent_analytic.py
  tests\test_v050_crossed_automatic_hermite.py
  tests\test_v049_crossed_raw_q_kernel.py
  tests\test_v048_crossed_u_tq_bridge.py
  tests\test_v047_crossed_px.py
  tests\test_v046_crossed_qlinear.py
  tests\test_crossed_ladder.py
) do (
  set /a N+=1
  echo [!N!/8] %%F...
  "%PY%" -m pytest -q "%%F" > "%OUT%\test_!N!.log" 2>&1
  set "RC=!ERRORLEVEL!"
  type "%OUT%\test_!N!.log" >> "%MASTER%"
  echo.>> "%MASTER%"
  if not "!RC!"=="0" (
    set "FAIL=!RC!"
    goto :finish
  )
)

:finish
echo Exit code: !FAIL!> "%OUT%\exit_code.txt"
echo Completed: %DATE% %TIME%>> "%MASTER%"
echo Exit code: !FAIL!>> "%MASTER%"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1
echo.
echo Validation complete. Exit code: !FAIL!
echo Result ZIP: %OUT%.zip
exit /b !FAIL!
