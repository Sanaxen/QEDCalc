import hashlib,json,tempfile,unittest
from pathlib import Path
from examples import three_loop_vp05_native_packed_continue as m
class Tests(unittest.TestCase):
    def test_header(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.bin"
            data=b"VP05PACK4\n"+json.dumps(dict(meta={},cursor=0,rank=0,terms=0,keys=0)).encode()+b"\n"
            p.write_bytes(data)
            obj,sha=m.header(p,False)
            self.assertEqual(sha,hashlib.sha256(data).digest())
            p.write_bytes(data+sha)
            self.assertEqual(m.header(p)[0],obj)
            p.write_bytes(data+b"x"*32)
            with self.assertRaisesRegex(RuntimeError,"checksum"):m.header(p)
    def test_observed(self):
        self.assertEqual(sum(x[0] for x in m.OBS.values()),305000)
        self.assertEqual(m.CAP,120000000)
    def test_native_resume(self):
        import os,subprocess,time
        b=m.b;n=m.n;p=1000003
        a=(1,1,1,0,0,0,0,0,0,0,0,0)
        c=(2,1,1,0,0,0,0,0,0,0,0,0)
        d=(1,1,1,-1,0,0,0,0,0,0,0,0)
        rows=[{a:2,c:3},{a:4,c:6},{a:-1,d:7},{c:1,d:2}]
        meta=b.meta(69,5,0)
        with tempfile.TemporaryDirectory(dir=m.n.BASE/"output") as tmp:
            w=Path(tmp);exe=w/"native";src=w/"source.bin";inp=w/"raw.in";out=w/"payload";mf=w/"meta.json"
            conv=n.wslpath if os.name=="nt" else lambda x:str(x)
            prefix=["wsl","--exec"] if os.name=="nt" else []
            subprocess.run(prefix+["g++","-std=c++17","-O3","-Wall","-Wextra",conv(n.BASE/"examples"/"vp05_native_packed.cpp"),"-o",conv(exe)],check=True,timeout=120)
            store=b.Packed()
            lead,row=b.reduce(rows[0],store,p,b.CAP,time.monotonic()+30)
            store.add(0,lead,row.items())
            b.save(src,meta,1,store,0,0)
            original=n.sha(src)
            h,_=m.header(src)
            mf.write_text(json.dumps(meta,separators=(",",":")),encoding="ascii")
            with inp.open("wb") as f:
                for raw in rows[1:]:n.write_row(f,((b.c.key(k),v%p) for k,v in raw.items() if v%p))
            subprocess.run(prefix+[conv(exe),conv(src),conv(inp),conv(out),conv(mf),str(p),"1",str(h["rank"]),str(h["keys"]),str(h["terms"]),"4",str(m.CAP)],check=True,timeout=60)
            _,checksum=m.header(out,False)
            with out.open("ab") as f:f.write(checksum)
            cursor,actual,_,_=b.load(out,meta,p)
            for i,raw in enumerate(rows[1:],1):
                lead,row=b.reduce(raw,store,p,b.CAP,time.monotonic()+30)
                if lead is not None:store.add(i,lead,row.items())
            self.assertEqual(cursor,4)
            self.assertEqual(actual.selected,store.selected)
            self.assertEqual(actual.terms,store.terms)
            self.assertEqual({k:dict(actual.items(k)) for k in actual.piv},{k:dict(store.items(k)) for k in store.piv})
            self.assertEqual(n.sha(src),original)
if __name__=="__main__":unittest.main()

