"""Read-only Kira SYSTEM weight audit using an external GPL Kira weight codec.

The codec is NOT vendored into QEDCalc. Supply pyred_weight.py from
BootLoops-ai/kira/bootloops-tools (GPL-3.0-or-later) via --codec-file.
No Kira execution, no changes to source DB or 63-master candidate file.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import gzip
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
RUN = "kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_monitored_t1_r5s6d0_20261015_204016648"
CANDIDATE = ROOT / "output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_refined_masters.txt"
MATCH = re.compile(r"VP05_full\[([^\]]+)\]")

def load_codec(file):
    if not file.is_file():
        raise FileNotFoundError(f"External Kira GPL codec not found: {file}")
    spec=importlib.util.spec_from_file_location("external_kira_pyred_weight",file)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import codec module")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def parse_file_integrals(path):
    return [tuple(int(x) for x in m.group(1).split(",")) for m in MATCH.finditer(path.read_text(encoding="utf-8"))]

def system_ids(path):
    ids=set()
    heads=set()
    equation_count=0
    with gzip.open(path,"rt",encoding="utf-8") as handle:
        while (line:=handle.readline()):
            if line.strip()!="Eq":
                raise ValueError(f"unexpected SYSTEM marker {line!r}")
            head=int(handle.readline().strip())
            n=int(handle.readline().strip())
            heads.add(head)
            equation_count+=1
            for _ in range(n):
                terms=handle.readline().split()
                if len(terms)<4:
                    raise ValueError(f"malformed equation {equation_count}")
                ids.add((int(terms[2]),int(terms[3])))
    return ids,heads,equation_count

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codec-file",type=Path,required=True)
    p.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    a=p.parse_args()
    project=a.project.resolve()
    if not (project/"results/kira.db").is_file():
        p.error(f"Missing Kira database: {project}")
    m=load_codec(a.codec_file.resolve())
    bits,ordering=m.from_kiradb(str(project/"results/kira.db"))
    # The original sector-203 project was generated with top-level sector 203.
    # Read and check rather than guessing any future project's settings.
    cfg=(project/"config/integralfamilies.yaml").read_text(encoding="utf-8")
    if not re.search(r"top_level_sectors:\s*\[\s*203\s*\]",cfg):
        p.error("Expected declared top-level sector 203")
    codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    if ordering!=5:
        p.error(f"Expected --integral_ordering=5, database has {ordering}")
    candidates=parse_file_integrals(CANDIDATE)
    targets=[x for x in candidates if m.sec_of(x)==203]
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    if len(targets)!=4 or len(masters)!=10:
        p.error("Expected 4 sector-203 candidates and 10 recorded masters")
    folder=project/"tmp/VP05_full"
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"))
    ids=set()
    heads=set()
    numeq=0
    for file in files:
        a_ids,a_heads,count=system_ids(file)
        ids.update(a_ids)
        heads.update(a_heads)
        numeq+=count
    if numeq!=3317:
        p.error(f"Saved SYSTEM equation count changed: {numeq} != 3317")
    errors=[]
    decoded=set()
    for weight,sec in ids:
        try:
            powers=codec.decode(weight)
            if m.sec_of(powers)!=sec or codec.encode(powers)!=weight:
                errors.append({"weight":weight,"sector":sec,"decoded":powers})
            decoded.add(powers)
        except (ValueError,AssertionError) as ex:
            errors.append({"weight":weight,"sector":sec,"error":str(ex)})
    report={"project":str(project),"external_codec":str(a.codec_file.resolve()),
        "ordering":ordering,"weight_bits":bits,"top_level_sector":203,
        "equations":numeq,"term_weight_sector_pairs":len(ids),
        "decoded_distinct_integrals":len(decoded),
        "decoding_errors":len(errors),"error_examples":errors[:5],
        "sector203_candidates":[{
            "integral":"VP05_full["+",".join(map(str,x))+"]",
            "weight":codec.encode(x),
            "appears_in_selected_system":x in decoded,
            "appears_as_equation_head":codec.encode(x) in heads,
            "in_kira_master_list":x in masters} for x in targets],
        "kira_masters_present_in_selected_system":sum(x in decoded for x in masters),
        "conclusion":"presence/absence only; no linear algebra reduction or r7s6d2 closure proven"}
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if errors:
        raise SystemExit("FAIL: codec mismatch, do not interpret candidate classifications")

if __name__=="__main__":
    main()
