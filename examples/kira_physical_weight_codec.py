"""Permutation-aware wrapper around an externally supplied Kira weight codec.

Physical indices are in input YAML order. Permutation is the zero-based
internal-to-input mapping from the SAME run's auxiliary.yaml.
No default identity assumption, no guessing custom preferred-master IDs.
The external codec is not vendored.
"""
import re

def sector(indices):
    return sum(1<<i for i,x in enumerate(indices) if x>0)

def read_permutation(text,family,np):
    # Require an explicit, unique family record in Kira's emitted format.
    records=re.split(r'^\s*-\s*name:\s*',text,flags=re.M)[1:]
    matches=[]
    for record in records:
        lines=record.splitlines()
        if not lines or lines[0].strip().strip('"\'')!=family:continue
        values=re.findall(r'^\s*permutation:\s*\[([^\]]+)\]',record,re.M)
        if len(values)!=1:raise ValueError("Missing or ambiguous permutation")
        matches.append(tuple(int(x.strip()) for x in values[0].split(",")))
    if len(matches)!=1:raise ValueError("Missing or ambiguous family")
    perm=matches[0]
    if len(perm)!=np or sorted(perm)!=list(range(np)):raise ValueError("Invalid zero-based permutation")
    return perm

class PhysicalWeightCodec:
    def __init__(self,module,*,np,bits,iord,topsectors,permutation):
        self.permutation=tuple(permutation)
        self.np=np
        if len(self.permutation)!=np or sorted(self.permutation)!=list(range(np)):
            raise ValueError("Invalid permutation")
        if not topsectors or any(not 0<t<(1<<np) for t in topsectors):raise ValueError("Invalid top sectors")
        self.internal_tops=[sum(1<<i for i,j in enumerate(self.permutation) if t&(1<<j)) for t in topsectors]
        self.codec=module.WeightCodec(np=np,bits=bits,iord=iord,topsectors=self.internal_tops)
    def to_internal(self,indices):
        if len(indices)!=self.np:raise ValueError("Index length")
        return tuple(indices[j] for j in self.permutation)
    def to_physical(self,indices):
        if len(indices)!=self.np:raise ValueError("Index length")
        out=[0]*self.np
        for i,j in enumerate(self.permutation):out[j]=indices[i]
        return tuple(out)
    def encode(self,indices):
        ex=tuple(indices)
        weight=self.codec.encode(self.to_internal(ex))
        if self.to_physical(self.codec.decode(weight))!=ex:raise ValueError("Codec roundtrip")
        return weight
    def decode_default(self,weight):
        """Caller must establish that weight is NOT a custom master ID."""
        ex=self.to_physical(self.codec.decode(weight))
        if self.encode(ex)!=weight:raise ValueError("Codec roundtrip")
        return ex
    def decode_key(self,key,*,custom_keys):
        key=tuple(key)
        if key in custom_keys:raise ValueError("Custom weight is not a default weight")
        ex=self.decode_default(key[0])
        if sector(ex)!=key[1]:raise ValueError("Recorded physical sector mismatch")
        return ex
