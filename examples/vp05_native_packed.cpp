// VP05 bounded native batch finite-field sparse reducer.
// Input/output little endian, 80-bit full keys; no production writes.
#include <cstdint>
#include <iostream>
#include <fstream>
#include <map>
#include <unordered_map>
#include <vector>
#include <stdexcept>
#include <chrono>
#include <string>
#include <algorithm>
using K=unsigned __int128;
using U=uint32_t;
using Row=std::map<K,U>;
struct Hash { size_t operator()(K k) const {
    return std::hash<uint64_t>{}(uint64_t(k)) ^ (std::hash<uint64_t>{}(uint64_t(k>>64))<<1);
}};
using Pivot=std::vector<std::pair<K,U>>;
static constexpr U FILL=20000, CAP=120000000;
static uint64_t peak_ram=0,peak_swap=0;
static bool warned=false;
static auto start=std::chrono::steady_clock::now();
void guard(){
    if(std::chrono::steady_clock::now()-start>std::chrono::minutes(25)) throw std::runtime_error("native time cap");
    std::ifstream f("/proc/meminfo");
    std::string line; uint64_t total=0,avail=0,st=0,sf=0;
    while(std::getline(f,line)){
        auto read=[&](const char* name,uint64_t& v){std::string n(name);if(line.rfind(n,0)==0)v=std::stoull(line.substr(n.size()));};
        read("MemTotal:",total);read("MemAvailable:",avail);read("SwapTotal:",st);read("SwapFree:",sf);
    }
    if(total>=avail && st>=sf){peak_ram=std::max(peak_ram,total-avail);peak_swap=std::max(peak_swap,st-sf);}
    if(!warned && (peak_ram>=18ull*1024*1024 || peak_swap>=30000000000ull/1024)){std::cerr<<"native memory warning\n";warned=true;}
    if(!total || !avail || avail>total || sf>st || total-avail>=22ull*1024*1024 || st-sf>=50000000000ull/1024)
        throw std::runtime_error("native memory guard");
}
K get(std::istream& f,unsigned n){
    K x=0; for(unsigned i=0;i<n;++i){int c=f.get();if(c==EOF)throw std::runtime_error("truncated input");x|=K(unsigned(c))<<(8*i);}return x;
}
void put(std::ostream& f,K x,unsigned n){for(unsigned i=0;i<n;++i)f.put(char((x>>(8*i))&255));if(!f)throw std::runtime_error("output error");}
Row readrow(std::istream& f,U p){
    U n=get(f,4);if(n>FILL)throw std::runtime_error("fill cap");
    Row r;for(U i=0;i<n;++i){K k=get(f,10);U v=get(f,4);if(!v||v>=p||!r.emplace(k,v).second)throw std::runtime_error("bad term");}return r;
}
void writerow(std::ostream& f,const Row& r){put(f,r.size(),4);for(auto [k,v]:r){put(f,k,10);put(f,v,4);}}
U power(U a,U n,U p){uint64_t r=1,b=a;while(n){if(n&1)r=r*b%p;b=b*b%p;n>>=1;}return U(r);}

#include <unordered_set>
#include <filesystem>
#include <sstream>
using Pair=std::pair<U,U>;
struct Record { U index,lead; std::vector<Pair> data; };
struct Store {
    std::vector<K> keys;
    std::unordered_map<K,U,Hash> ids;
    std::vector<Record> rows;
    std::unordered_map<K,size_t,Hash> lookup;
    uint64_t terms=0;
    U intern(K k){
        auto i=ids.find(k);if(i!=ids.end())return i->second;
        if(keys.size()>=10000000)throw std::runtime_error("key cap");
        U id=keys.size();keys.push_back(k);ids.emplace(k,id);return id;
    }
};
bool canonical(K k){
    K code=k&((K(1)<<60)-1),v=code;unsigned t=0,r=0,s=0;
    for(int i=0;i<12;++i){int a=int(v&31)-16;v>>=5;if(a>0){++t;r+=a;}else s-=a;}
    return k==((K((t*64+r)*64+s)<<60)|code);
}
void load(std::istream& f,Store& st,U p,U cursor,U rank,U keys,uint64_t terms){
    std::string magic,header;std::getline(f,magic);std::getline(f,header);
    if(magic!="VP05PACK4"||header.empty()||header.size()>1048576||rank>cursor||keys>terms||terms>CAP||keys>10000000)throw std::runtime_error("packed header");
    for(U i=0;i<keys;++i){
        if(i%10000==0)guard();
        K k=get(f,10);if(!canonical(k)||st.ids.count(k))throw std::runtime_error("packed key");
        st.intern(k);
    }
    U last=0;
    for(U i=0;i<rank;++i){
        if(i%256==0)guard();
        U idx=get(f,4),lead=get(f,4),n=get(f,4);
        if(idx>=cursor||(i&&idx<=last)||lead>=keys||!n||n>FILL||st.terms+n>terms)throw std::runtime_error("packed row header");
        last=idx;Record row{idx,lead,{}};row.data.resize(n);
        std::unordered_set<U> seen;bool has=false;
        for(auto& x:row.data){x.first=get(f,4);if(x.first>=keys||!seen.insert(x.first).second||st.keys[x.first]>st.keys[lead])throw std::runtime_error("packed id");}
        for(auto& x:row.data){x.second=get(f,4);if(!x.second||x.second>=p)throw std::runtime_error("packed coef");if(x.first==lead){has=true;if(x.second!=1)throw std::runtime_error("packed normalization");}}
        if(!has||!st.lookup.emplace(st.keys[lead],st.rows.size()).second)throw std::runtime_error("packed lead");
        st.terms+=n;st.rows.push_back(std::move(row));
    }
    if(st.terms!=terms)throw std::runtime_error("packed term count");
    for(int i=0;i<32;++i)get(f,1); // Python verifies SHA256 before and after use
    if(f.peek()!=EOF)throw std::runtime_error("packed trailing bytes");
}
void save(const std::string& path,const Store& st,U cursor,const std::string& meta){
    std::ofstream f(path,std::ios::binary|std::ios::trunc);
    if(!f)throw std::runtime_error("checkpoint open");
    f<<"VP05PACK4\n{\"meta\":"<<meta<<",\"cursor\":"<<cursor<<",\"rank\":"<<st.rows.size()<<",\"terms\":"<<st.terms<<",\"keys\":"<<st.keys.size()<<",\"peak\":0,\"elapsed\":0}\n";
    for(auto k:st.keys)put(f,k,10);
    for(const auto& row:st.rows){
        put(f,row.index,4);put(f,row.lead,4);put(f,row.data.size(),4);
        for(auto x:row.data)put(f,x.first,4);
        for(auto x:row.data)put(f,x.second,4);
    }
    f.flush();if(!f)throw std::runtime_error("checkpoint flush");
}
int main(int argc,char**argv){
    try{
        // source, raw input, output payload, meta file, p,cursor,rank,keys,terms,end,cap
        if(argc!=12)throw std::runtime_error("argument count");
        U p=std::stoul(argv[5]),cursor=std::stoul(argv[6]),rank=std::stoul(argv[7]),keys=std::stoul(argv[8]),end=std::stoul(argv[10]);
        uint64_t terms=std::stoull(argv[9]),cap=std::stoull(argv[11]);
        if((p!=1000003&&p!=1000033)||end<cursor||end-cursor>5000||cap>CAP||terms>cap)throw std::runtime_error("scope");
        Store st;guard();
        if(std::string(argv[1])!="-"){std::ifstream f(argv[1],std::ios::binary);if(!f)throw std::runtime_error("source open");load(f,st,p,cursor,rank,keys,terms);}
        else if(cursor||rank||keys||terms)throw std::runtime_error("empty source mismatch");
        std::ifstream in(argv[2],std::ios::binary),mf(argv[4]);std::string meta;std::getline(mf,meta);
        if(!in||meta.empty()||meta.size()>1048576)throw std::runtime_error("input open");
        for(;cursor<end;++cursor){
            guard();Row r=readrow(in,p);for(auto x:r)if(!canonical(x.first))throw std::runtime_error("raw key");
            U steps=0;
            while(!r.empty()){
                if(r.size()>FILL)throw std::runtime_error("fill cap");
                K lead=r.rbegin()->first;U factor=r.rbegin()->second;
                auto it=st.lookup.find(lead);
                if(it==st.lookup.end()){
                    if(st.terms+r.size()>cap)throw std::runtime_error("term cap");
                    U inv=power(factor,p-2,p);
                    Record row{cursor,st.intern(lead),{}};row.data.reserve(r.size());
                    for(auto x:r)row.data.emplace_back(st.intern(x.first),uint64_t(x.second)*inv%p);
                    st.terms+=r.size();st.lookup.emplace(lead,st.rows.size());st.rows.push_back(std::move(row));break;
                }
                for(auto x:st.rows[it->second].data){
                    K k=st.keys[x.first];auto pos=r.find(k);U old=pos==r.end()?0:pos->second;
                    U val=(uint64_t(old)+p-uint64_t(factor)*x.second%p)%p;
                    if(val){if(pos==r.end())r.emplace(k,val);else pos->second=val;}else if(pos!=r.end())r.erase(pos);
                }
                if(++steps%256==0)guard();
            }
        }
        if(in.peek()!=EOF)throw std::runtime_error("trailing raw input");
        guard();save(argv[3],st,cursor,meta);
        std::cout<<"VP05_NATIVE08_CPP rows="<<cursor<<" rank="<<st.rows.size()<<" terms="<<st.terms<<" peak_ram_kib="<<peak_ram<<" peak_swap_kib="<<peak_swap<<std::endl;
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
