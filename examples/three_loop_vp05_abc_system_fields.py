"""Read-only inventory of complete SYSTEM records and SQLite metadata."""
import argparse
import json
import sqlite3
import time
from pathlib import Path
from collections import Counter, defaultdict
from examples import three_loop_vp05_abc_mapping_audit as a

ROOT=a.n.BASE/"output"/"vp05_abc_system_fields32"
SOURCE=a.ROOT/"report_1795816223575427600.json"
SHA="7078388862843f93e9bf9116317f86d0c3bc6e1259cddfe06d945567496015a4"

def inventory(records):
    fields=[Counter() for _ in range(6)]
    bykey=defaultdict(set)
    for terms in records:
        for t in terms:
            if len(t)!=6:raise RuntimeError("Expected six SYSTEM fields")
            for i,x in enumerate(t):fields[i][x]+=1
            bykey[(t[2],t[3])].add((t[0],t[4],t[5]))
    return {"fields":[{"field":i+1,"distinct":len(c),"examples":c.most_common(20)} for i,c in enumerate(fields)],
            "auxiliary_by_key":[{"key":list(k),"auxiliary":[list(v) for v in sorted(s)]} for k,s in sorted(bykey.items())]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic()
    if a.n.sha(SOURCE)!=SHA:raise RuntimeError("Mapping report SHA")
    data=a.gap.read(SOURCE)
    if data["status"]!="VP05_ABC_MAPPING_AUDIT_NOT_PROOF":raise RuntimeError("Mapping scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(a.n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P
    selected={r["id"] for r in data["result"]["checks"]}
    if len(selected)!=389:raise RuntimeError("Selected scope")
    rows=[];allrows=[];idx=0
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            if time.monotonic()-start>args.hours*3600:raise TimeoutError("Inventory budget")
            allrows.append(terms)
            if idx in selected:rows.append({"id":idx,"file":path.name,"ordinal":ordinal,"head":head,"terms":terms})
            idx+=1
    if idx!=2678 or len(rows)!=389:raise RuntimeError("SYSTEM scope")
    db=project/"results/kira.db"
    if db not in pins:raise RuntimeError("Unpinned database")
    tables=[]
    with sqlite3.connect(db.resolve().as_uri()+"?mode=ro&immutable=1",uri=True) as conn:
        conn.execute("PRAGMA query_only=ON")
        for name,sql in conn.execute("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name"):
            quoted='"'+name.replace('"','""')+'"'
            info=list(conn.execute("PRAGMA table_info("+quoted+")"))
            sample=list(conn.execute("SELECT * FROM "+quoted+" LIMIT 3"))
            def safe(v):return {"blob_hex_prefix":v[:128].hex(),"bytes":len(v)} if isinstance(v,bytes) else v
            tables.append({"name":name,"schema":sql,"columns":[list(x) for x in info],"sample":[[safe(v) for v in r] for r in sample]})
    inv=inventory([r["terms"] for r in rows])
    opaque=[r for r in rows if any((t[2],t[3]) in {("4","73"),("5","201")} for t in r["terms"])]
    payload={"status":"VP05_ABC_SYSTEM_FIELDS_INVENTORY_NOT_PROOF","inputs":{str(k):v for k,v in pins.items()},
             "selected_rows":rows,"selected_inventory":inv,"all_inventory":inventory(allrows),
             "opaque_rows":opaque,"database_tables":tables,"config_text":data["result"]["config_text"],
             "physical_mapping_verified":False,"full_closure_proven":False}
    # Ensure nested tuples from Counter and SQLite are JSON-normalized.
    payload=json.loads(json.dumps(payload))
    if any(a.n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True)
    dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],rows=len(rows),system_rows=idx,opaque_rows=len(opaque),
            field_summary=payload["selected_inventory"]["fields"],
            opaque_auxiliary=[r for r in inv["auxiliary_by_key"] if r["key"] in [["4","73"],["5","201"]]],
            database_schema=[{"name":t["name"],"schema":t["schema"],"columns":t["columns"]} for t in tables],
            representative_rows=rows[:3],representative_opaque_rows=opaque[:2],
            config_text=payload["config_text"],report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,
            inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
