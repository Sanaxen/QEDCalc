"""Read-only Kira DB schema inventory for mapping small SYSTEM IDs.

Uses SQLite mode=ro, PRAGMA query_only and a bounded schema search.
Never assumes an arbitrary DB integer is an integral/master ID.
"""
from __future__ import annotations
import argparse,json,sqlite3
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_kiradb_id_schema_audit.json"))
    a=p.parse_args();db=(a.project/"results/kira.db").resolve()
    if not db.is_file():p.error("Missing kira.db")
    con=sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)
    con.execute("PRAGMA query_only=ON")
    try:
        rows=con.execute("SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
        objects=[]
        for name,kind,ddl in rows:
            if name.startswith("sqlite_"):continue
            qname='"'+name.replace('"','""')+'"'
            cols=con.execute("PRAGMA table_info("+qname+")").fetchall()
            objects.append({"name":name,"type":kind,"columns":[{"name":c[1],"type":c[2],"pk":bool(c[5])} for c in cols],
              "ddl_excerpt":(ddl or "")[:1500],
              "potential_id_related":any(x in (name+" "+str(cols)).lower() for x in ("master","integral","weight","sector","identity","mapping"))})
        report={"db":str(db),"objects":objects,"potential_objects":[o["name"] for o in objects if o["potential_id_related"]],
          "small_id_mapping_verified":False,"data_rows_read":0,
          "warning":"Schema-level discovery only. Do not infer a mapping from table or column names."}
    finally:con.close()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_KIRADB_ID_SCHEMA "+json.dumps({k:v for k,v in report.items() if k!="objects"}|
      {"objects":objects[:30],"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
