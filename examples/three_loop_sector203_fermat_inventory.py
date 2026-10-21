"""Read-only, bounded Fermat executable inventory for isolated Kira testing."""
from __future__ import annotations
import argparse, json, os, re, shutil
from pathlib import Path

PATTERN = re.compile(r"^(fermat|fer64|fermat64|fer[0-9]+|fermat[-_].*)$", re.I)
SKIP = {".git", ".cache", ".local", "node_modules", "output", "results", "tmp"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("output/three_loop_integral_family_audit/vp05_fermat_inventory.json"))
    a = p.parse_args()
    roots = [Path("/usr/local/bin"), Path("/usr/bin"), Path("/opt"),
             Path.home() / "bin", Path.home() / "Fermat",
             Path.home() / "fermat", Path("/usr/local/fermat")]
    names = ("fermat", "fer64", "fermat64")
    candidates = []
    env_path = os.environ.get("FERMATPATH")
    if env_path: candidates.append(Path(env_path))
    for n in names:
        found = shutil.which(n)
        if found: candidates.append(Path(found))
    count = 0
    truncated = False
    for root in roots:
        if not root.is_dir(): continue
        for base, dirs, files in os.walk(root, followlinks=False):
            depth = len(Path(base).relative_to(root).parts)
            dirs[:] = sorted(d for d in dirs if d not in SKIP and not d.startswith(".")) if depth < 3 else []
            for name in files:
                count += 1
                if PATTERN.fullmatch(name): candidates.append(Path(base) / name)
                if count >= 25000:
                    truncated = True
                    break
            if truncated: break
        if truncated: break
    seen = set()
    matches = []
    for candidate in candidates:
        try:
            path = candidate.resolve()
            if str(path) in seen: continue
            seen.add(str(path))
            matches.append({"path": str(path), "is_file": path.is_file(),
                            "executable": path.is_file() and os.access(path, os.X_OK)})
        except (OSError, RuntimeError) as error:
            matches.append({"path": str(candidate), "error": type(error).__name__})
    result = {
        "status": "EXECUTABLE_CANDIDATES_FOUND" if any(x.get("executable") for x in matches) else "FERMAT_NOT_LOCATED_IN_SEARCH_SCOPE",
        "fermatpath": env_path, "path_lookups": {n: shutil.which(n) for n in names},
        "candidates": matches, "roots_searched": [str(root) for root in roots],
        "scanned_files": count, "scan_truncated": truncated,
        "kira_executed": False, "vp05_project_opened": False,
        "note": "Read-only bounded search; custom paths and Windows drives are not scanned. Missing does not imply uninstalled."
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("VP05_FERMAT_INVENTORY " + json.dumps(result, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
