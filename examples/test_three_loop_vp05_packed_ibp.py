import random,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from examples import three_loop_vp05_packed_ibp as p
c=p.c

class PackedTests(unittest.TestCase):
    def test_equivalence(self):
        rng=random.Random(123)
        keys=[(1,i,0,0,0,0,0,0,0,0,0,0) for i in range(-6,7)]
        old={};new=p.Packed();stored=0
        for i in range(100):
            raw={k:rng.randrange(101) for k in rng.sample(keys,4)}
            lead,v=c.reduce_row(raw,old,101,stored)
            a,b=p.reduce(raw,new,101,p.CAP)
            self.assertEqual((a,b),(lead,v))
            if lead is not None:
                old[lead]=v;stored+=len(v);new.add(i,a,b.items())
        self.assertEqual(new.terms,stored)
        self.assertEqual({k:dict(new.items(k)) for k in new.piv},old)
    def test_binary(self):
        s=p.Packed();k=c.key((1,)*12);s.add(0,k,[(k,1)])
        with tempfile.TemporaryDirectory() as d,patch.object(p.a,"memory",return_value=(32*p.a.GIB,20*p.a.GIB)),patch.object(p.shutil,"disk_usage") as disk:
            disk.return_value.free=10*p.a.GIB
            f=Path(d)/"x.bin";m=p.meta(69,4,0)
            p.save(f,m,1,s,10,1)
            cursor,r,peak,elapsed=p.load(f,m,101)
            self.assertEqual((cursor,r.terms,dict(r.items(k)),peak,elapsed),(1,1,{k:1},10,1))
            with f.open("ab") as out:out.write(b"x")
            with self.assertRaises(RuntimeError):p.load(f,m,101)
