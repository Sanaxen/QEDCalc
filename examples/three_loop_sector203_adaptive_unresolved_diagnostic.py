"""Classify 41 unresolved VP05 adaptive certificate fits without refitting.

Uses existing per-row trial counters and verified sample provenance.
This is an accounting diagnostic, not a higher-degree or exact proof.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
DEFAULT=Path("output/three_loop_integral_family_audit/vp05_certificate_adaptive_degree.json")
SAMPLES=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples_grid_v2.json")
OUT=Path("output/three_loop_integral_family_audit/vp05_adaptive_unresolved_diagnostic.json")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--adaptive",type=Path,default=DEFAULT)
    ap.add_argument("--samples",type=Path,default=SAMPLES)
    ap.add_argument("--output",type=Path,default=OUT)
    a=ap.parse_args()
    archive=a.samples.read_bytes()
    result=json.loads(a.adaptive.read_text(encoding="utf-8-sig"))
    source=json.loads(archive.decode("utf-8-sig"))
    summary=result["summary"]
    if hashlib.sha256(archive).hexdigest()!=summary["source_sha256"]:
        ap.error("Adaptive result does not belong to the supplied sample archive")
    if source.get("source_sha256")!=summary.get("equations_sha256"):
        ap.error("Compressed equation digest mismatch")
    entries=result.get("results",[])
    if len(entries)!=166 or {x["row"] for x in entries}!=set(range(166)):
        ap.error("Invalid adaptive result rows")
    unresolved=[x for x in entries if x["status"]=="unresolved"]
    if len(unresolved)!=summary["unresolved"]:
        ap.error("Unresolved count mismatch")
    groups={"only_nonunique":[],"only_holdout_failure":[],"both":[],"other":[]}
    for x in unresolved:
        n=x["nonunique"];f=x["holdout_failures"]
        label="both" if n and f else "only_nonunique" if n else "only_holdout_failure" if f else "other"
        groups[label].append(x["row"])
    report={"source_sha256":summary["source_sha256"],"rows":166,
            "unresolved":len(unresolved),
            "groups":groups,"counts":{k:len(v) for k,v in groups.items()},
            "notes":"Categories describe attempted models, not the mathematical cause; an individual row may have both nonunique and failed models.",
            "fermat_executed":False,"proof":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_UNRESOLVED_DIAGNOSTIC "+json.dumps({k:v for k,v in report.items() if k!="groups"} | {"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
