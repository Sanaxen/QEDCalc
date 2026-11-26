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
static constexpr U FILL=20000, CAP=60000000;
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
    if(!warned && (peak_ram>=18ull*1024*1024 || peak_swap>=4ull*1024*1024)){std::cerr<<"native memory warning\n";warned=true;}
    if(!total || !avail || avail>total || sf>st || total-avail>=22ull*1024*1024 || st-sf>=8ull*1024*1024)
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
int main(int argc,char**argv){
    try{
        if(argc!=3)throw std::runtime_error("input output required");
        guard();
        std::ifstream in(argv[1],std::ios::binary);std::ofstream out(argv[2],std::ios::binary|std::ios::trunc);
        if(!in||!out)throw std::runtime_error("open failed");
        if(get(in,4)!=0x31425056)throw std::runtime_error("magic");
        U p=get(in,4),n=get(in,4),batch=get(in,4);
        if((p!=1000003 && p!=1000033)||n>1000000||batch>5000)throw std::runtime_error("scope");
        std::unordered_map<K,Pivot,Hash> piv;uint64_t terms=0;
        for(U i=0;i<n;++i){
            if(i%256==0)guard();
            Row r=readrow(in,p);if(r.empty()||r.rbegin()->second!=1)throw std::runtime_error("bad pivot");
            terms+=r.size();if(terms>CAP||!piv.emplace(r.rbegin()->first,Pivot(r.begin(),r.end())).second)throw std::runtime_error("pivot cap/duplicate");
        }
        auto t=std::chrono::steady_clock::now();put(out,0x31425056,4);put(out,batch,4);
        for(U i=0;i<batch;++i){
            guard();Row r=readrow(in,p);U steps=0;
            while(!r.empty()){
                if(r.size()>FILL)throw std::runtime_error("fill cap");
                auto lead=r.rbegin()->first;U factor=r.rbegin()->second;
                auto it=piv.find(lead);
                if(it==piv.end()){
                    if(terms+r.size()>CAP)throw std::runtime_error("term cap");
                    U inv=power(factor,p-2,p);for(auto& kv:r)kv.second=uint64_t(kv.second)*inv%p;
                    terms+=r.size();piv.emplace(lead,Pivot(r.begin(),r.end()));break;
                }
                for(auto [k,v]:it->second){
                    auto pos=r.find(k);U old=pos==r.end()?0:pos->second;
                    U x=(uint64_t(old)+p-uint64_t(factor)*v%p)%p;
                    if(x){if(pos==r.end())r.emplace(k,x);else pos->second=x;}else if(pos!=r.end())r.erase(pos);
                }
                if(++steps%256==0)guard();
            }
            writerow(out,r);put(out,piv.size(),4);put(out,terms,8);
        }
        if(in.peek()!=EOF)throw std::runtime_error("trailing input");
        put(out,std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-t).count(),8);
        guard();put(out,peak_ram,8);put(out,peak_swap,8);
        out.flush();if(!out)throw std::runtime_error("flush");
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
