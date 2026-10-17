"""Read-only scan for saved exact low-term relations among candidate4 and masters.

No Kira execution, no symbolic elimination. Reports direct serialized identities
only and does not infer an identity when none is found.
"""
from __future__ import annotations

import argparse
import gzip
from collections import Counter
from pathlib import Path

from examples.three_loop_sector203_weight_audit import ROOT

DEFAULT = ROOT / "output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
TARGET = (10, 203)
ALLOW = {(5, 201), (6, 203), TARGET}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=DEFAULT)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    paths = sorted((args.project / "tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(paths) != 14:
        parser.error(f"Expected 14 SYSTEM files, got {len(paths)}")
    matched, containing, direct = 0, 0, []
    size_hist = Counter()
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            while True:
                marker = stream.readline()
                if not marker:
                    break
                if marker.strip() != "Eq":
                    raise ValueError(f"Bad equation marker in {path}")
                label = stream.readline().strip()
                n = int(stream.readline().strip())
                terms = []
                for _ in range(n):
                    parts = stream.readline().split()
                    if len(parts) < 4:
                        raise ValueError("Bad SYSTEM term")
                    terms.append(((int(parts[2]), int(parts[3])), parts[1]))
                matched += 1
                keys = {key for key, coeff in terms}
                if TARGET in keys:
                    containing += 1
                    size_hist[len(terms)] += 1
                    if keys.issubset(ALLOW):
                        direct.append((path.name, label, terms))
    print(f"EQUATIONS={matched} CONTAIN_TARGET={containing} DIRECT_REDUCTIONS={len(direct)}")
    print(f"TARGET_EQUATION_TERM_COUNTS={dict(sorted(size_hist.items()))}")
    for name, label, terms in direct[:args.limit]:
        print(f"DIRECT {name} Eq={label} " + " + ".join(f"({coeff})*{key}" for key, coeff in terms))
    if not direct:
        print("No direct 2-master relation in saved single equations; symbolic elimination or reconstruction is required.")


if __name__ == "__main__":
    main()
