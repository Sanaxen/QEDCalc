"""Read-only inventory of Kira SYSTEM files; no undocumented ID decoding."""
import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_monitored_t1_r5s6d0_"

def inspect(path):
    equations = 0
    terms = 0
    internal_sectors = Counter()
    ids = set()
    examples = []
    malformed = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
        while True:
            marker = handle.readline()
            if not marker:
                break
            if marker.strip() != "Eq":
                malformed += 1
                break
            head = handle.readline().strip()
            number = handle.readline().strip()
            try:
                n = int(number)
                if n < 0 or n > 1000000:
                    raise ValueError("invalid equation size")
            except ValueError:
                malformed += 1
                break
            eq_terms = []
            for _ in range(n):
                line = handle.readline()
                fields = line.split()
                if len(fields) < 4:
                    malformed += 1
                    break
                eq_terms.append(fields)
                try:
                    ids.add(fields[2])
                    internal_sectors[fields[3]] += 1
                except IndexError:
                    malformed += 1
            if len(examples) < 2:
                examples.append({"head": head, "term_count": n, "first_term": eq_terms[0] if eq_terms else None})
            equations += 1
            terms += len(eq_terms)
    return {"file":path.name, "compressed_bytes":path.stat().st_size,
            "equations":equations, "terms":terms, "unique_internal_ids":len(ids),
            "term_sector_distribution":dict(sorted(internal_sectors.items(),key=lambda p:int(p[0]))),
            "sample_equations":examples,"parse_errors":malformed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path)
    a=p.parse_args()
    dirs=sorted((ROOT/"output").glob(PREFIX+"*"))
    project=a.project or (dirs[-1] if dirs else None)
    if project is None:
        p.error("completed project not found")
    folder=project/"tmp"/"VP05_full"
    if not folder.is_dir():
        p.error(f"SYSTEM folder missing: {folder}")
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"), key=lambda p:int(p.stem.split("_")[-1].split(".")[0]))
    if not files:
        p.error("no SYSTEM files found")
    rows=[inspect(f) for f in files]
    print(json.dumps({"project":str(project),"files":rows,
      "total_equations":sum(r["equations"] for r in rows),
      "total_terms":sum(r["terms"] for r in rows),
      "scope":"read-only; internal integral identifiers are NOT decoded, nor is target reducibility inferred",
      "status":"SYSTEM contents inventoried; next step is to verify Kira ID encoding before candidate-ID matching"},
      indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
