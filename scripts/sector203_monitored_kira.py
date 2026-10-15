"""Run isolated Kira with RAM/swap/process metrics and hard resource guard (WSL Python3)."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

def memory():
    d = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
                d[key] = int(val.strip().split()[0]) * 1024
    return d

def cpu(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        rest = stat.rsplit(")", 1)[1].split()
        return int(rest[11]) + int(rest[12])
    except (OSError, ValueError, IndexError):
        return None

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--warn-gib", type=float, default=210)
    a.add_argument("--stop-gib", type=float, default=220)
    a.add_argument("--max-seconds", type=int, default=1800)
    a.add_argument("--interval", type=int, default=5)
    args = a.parse_args()
    if not (0 < args.warn_gib < args.stop_gib <= 240):
        a.error("require 0 < warn-gib < stop-gib <= 240")
    if args.max_seconds < 10 or args.interval < 1:
        a.error("invalid duration/interval")
    project = Path.cwd()
    if not (project / "jobs.yaml").is_file():
        a.error("must run from Kira project root")
    for f in ("monitored_kira.log", "monitored_metrics.jsonl", "monitored_exit.json"):
        if (project / f).exists():
            a.error(f"refusing to overwrite {f}")
    before = memory()
    if (before["SwapTotal"] - before["SwapFree"]) >= args.stop_gib * 1024**3:
        a.error("swap already exceeds stop threshold")
    start = time.monotonic()
    reason = "kira_exit"
    last_sector = None
    warned = False
    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    cpu_prev = None
    try:
        with open("monitored_kira.log", "w", encoding="utf-8") as log, open(
            "monitored_metrics.jsonl", "w", encoding="utf-8"
        ) as metrics:
            proc = subprocess.Popen(
                ["kira", "--integral_ordering=5", "jobs.yaml"], stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True,
                env={**os.environ, "FERMATPATH": str(Path.home() / "fermat/Ferl7/fer64")},
            )
            while True:
                elapsed = time.monotonic() - start
                mem = memory()
                swap_gib = (mem["SwapTotal"] - mem["SwapFree"]) / 1024**3
                total_ram_gib = mem["MemTotal"] / 1024**3
                used_ram_gib = (mem["MemTotal"] - mem["MemAvailable"]) / 1024**3
                current_cpu = cpu(proc.pid)
                cpu_percent = None
                if cpu_prev is not None and current_cpu is not None:
                    cpu_percent = 100 * (current_cpu - cpu_prev[0]) / clock_ticks / max(
                        0.01, elapsed - cpu_prev[1]
                    )
                if current_cpu is not None:
                    cpu_prev = (current_cpu, elapsed)
                try:
                    # Only inspect the last 32 KiB; Kira's progress writes can be large.
                    with open("monitored_kira.log", "rb") as inp:
                        inp.seek(max(0, inp.seek(0, 2) - 32768))
                        tail = inp.read().decode("utf-8", "replace")
                    hits = re.findall(r"Generate equations for topology .*? sector (\d+) \((\d+) of (\d+)\)", tail)
                    if hits:
                        last_sector = hits[-1]
                except OSError:
                    pass
                sample = {
                    "elapsed_s": round(elapsed, 1),
                    "ram_used_gib": round(used_ram_gib, 2),
                    "ram_total_gib": round(total_ram_gib, 2),
                    "swap_used_gib": round(swap_gib, 2),
                    "swap_total_gib": round(mem["SwapTotal"] / 1024**3, 2),
                    "kira_main_cpu_percent": round(cpu_percent, 1) if cpu_percent is not None else None,
                    "last_sector": last_sector,
                }
                metrics.write(json.dumps(sample) + "\n")
                metrics.flush()
                print(json.dumps(sample), flush=True)
                code = proc.poll()
                if code is not None:
                    break
                if swap_gib >= args.stop_gib:
                    reason = "swap_stop"
                elif elapsed >= args.max_seconds:
                    reason = "time_stop"
                if swap_gib >= args.warn_gib and not warned:
                    print(f"WARNING: swap >= {args.warn_gib} GiB", flush=True)
                    warned = True
                if reason != "kira_exit":
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                    break
                time.sleep(args.interval)
            code = proc.wait()
        final = {"reason": reason, "kira_returncode": code, "elapsed_s": round(time.monotonic()-start,1),
                 "last_sector": last_sector, "success": reason == "kira_exit" and code == 0}
        Path("monitored_exit.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
        print("MONITOR_RESULT=" + json.dumps(final), flush=True)
        if final["success"]:
            return 0
        return 124 if reason == "time_stop" else 125 if reason == "swap_stop" else 1
    except BaseException:
        if "proc" in locals() and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
        raise

if __name__ == "__main__":
    raise SystemExit(main())
