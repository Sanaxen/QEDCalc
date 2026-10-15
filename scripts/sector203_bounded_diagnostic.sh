#!/usr/bin/env bash
set -u
if [ -e diagnostic_capture_v2.log ] || [ -e diagnostic_exit_v2.txt ]; then
  echo "ERROR: v2 diagnostic artifacts already exist; refusing overwrite" >&2
  exit 4
fi
export FERMATPATH="$HOME/fermat/Ferl7/fer64"
timeout --signal=TERM --kill-after=5s 90s kira --integral_ordering=5 jobs.yaml > diagnostic_capture_v2.log 2>&1
code=$?
printf '%s\n' "$code" > diagnostic_exit_v2.txt
printf 'KIRA_TIMEOUT_EXIT_CODE=%s\n' "$code"
tail -n 35 diagnostic_capture_v2.log
exit "$code"
