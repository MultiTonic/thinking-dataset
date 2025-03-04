import argparse,asyncio,logging,os,sys,time,multiprocessing,math
from concurrent.futures import ProcessPoolExecutor
from datasets import Dataset,DatasetDict,load_dataset
from rapidfuzz import fuzz
import pandas as pd
from tqdm.asyncio import tqdm as atqdm
from tqdm import tqdm
W=max(4,multiprocessing.cpu_count()-1)
L="logs"
B=500
T=4
P=False
M=2
R=5
def l(m,c=True):
    try:
        f.info(m)
        if c:
            if P:tqdm.write(f"[{time.strftime('%X')}] {m}")
            else:
                try:c_l.info(m)
                except UnicodeEncodeError:c_l.info(m.encode('ascii',errors='replace').decode('ascii'))
    except Exception as e:print(f"[LOGGING ERROR] {str(e)}")
def s_l(p):
    os.makedirs(p,exist_ok=True)
    c,f=logging.getLogger("c"),logging.getLogger("f")
    h=logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    c.addHandler(h)
    c.setLevel(logging.INFO)
    c.propagate=False
    n=os.path.join(p,f"fuzz_{int(time.time())}.log")
    h=logging.FileHandler(n,encoding='utf-8')
    h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    f.addHandler(h)
    f.setLevel(logging.INFO)
    f.propagate=False
    return c,f
def s_d(d,o=None):
    i=str(int(time.time()))
    d=os.path.abspath(d)
    e=os.path.join(o or os.getcwd(),"data")
    r=os.path.join(e,i)
    u=os.path.join(r,"fuzzed")
    p=os.path.join(r,"deduped")
    for x in[d,e,r,u,p]:os.makedirs(x,exist_ok=True)
    return{"run_id":i,"log_dir":d,"data_dir":e,"run_dir":r,"fuzzed_dir":u,"deduped_dir":p}
class S:
    def __init__(s):
        s.s=time.time()
        s.t=s.r=s.p=0
        s.l=time.time()
    def l_s(s,n,o,c):
        s.t+=o
        s.r+=(o-c)
        s.p+=1
    def g_s(s):
        e=time.time()-s.s
        r=(s.r/s.t*100)if s.t>0 else 0
        p=s.t/e if e>0 else 0
        return f"TELEMETRY: {s.t:,}r in {e:.1f}s • {s.r:,}r ({r:.1f}%) • {p:.1f}r/s • {s.p}s"
async def l_s(s):
    try:
        l(f"Loading {s}")
        d=load_dataset(s)
        if isinstance(d,Dataset):
            r=len(d)
            l(f"Loaded 1 split with {r} records")
            return{"default":d},{"default":r}
        c={s:len(d[s])for s in d}
        t=sum(c.values())
        l(f"Loaded {len(c)} splits with {t:,} records")
        for s,n in c.items():l(f"- {s}: {n:,}")
        return d,c
    except Exception as e:
        l(f"Error: {e}",False)
        raise
def s_b_l(d,c):
    r=d.to_list()
    if not r:return d
    l(f"Sorting by '{c}' length")
    df=pd.DataFrame(r)
    if c not in df.columns:return d
    df['_l']=df[c].astype(str).str.len()
    if df['_l'].isnull().any():df['_l']=df['_l'].fillna(0)
    df=df.sort_values(by='_l')
    n=df['_l'].min()
    x=df['_l'].max()
    df=df.drop('_l',axis=1)
    l(f"Sorted: {len(df)} records from {n} to {x}")
    return Dataset.from_pandas(df)
def dd(d,c):
    r=d.to_list()
    o=len(r)
    if o==0:return d,0
    l(f"Deduplicating {o:,} by '{c}'")
    df=pd.DataFrame(r)
    d=df.drop_duplicates(subset=[c])
    n=len(d)
    r=o-n
    p=(r/o*100)if o>0 else 0
    l(f"Removed {r:,} dupes ({p:.1f}%)")
    return Dataset.from_pandas(d),r
def p_b_s(d):
    b,c,t,s,e=d
    x=[str(r[c])for r in b]
    n=len(b)
    k=set(range(n))
    r=0
    for i in range(s,e):
        if i not in k:continue
        for j in range(i+1,n):
            if j not in k:continue
            if fuzz.token_sort_ratio(x[i],x[j])>=t:
                k.discard(j)
                r+=1
    return[u for u in k if s<=u<e],r
async def p_b_p(b,c,t,w):
    n=len(b)
    l(f"Batch: {n} with {w}")
    z=math.ceil(n/w)
    with ProcessPoolExecutor(max_workers=w) as executor:
        with tqdm(total=n,desc="Batch",leave=False) as p:
            o=asyncio.get_running_loop()
            k=set()
            r=0
            d=0
            for i in range(w):
                s=i*z
                e=min(s+z,n)
                if s>=n:break
                g=await o.run_in_executor(executor,p_b_s,(b,c,t,s,e))
                v,m=g
                k.update(v)
                r+=m
                d+=1
                p.update(e-s)
                p.set_description(f"Batch ({d}/{w})")
    q=[b[i]for i in sorted(k)]
    u=len(q)
    v=n-u
    if v>0:l(f"Kept {u}/{n} ({v} removed)")
    return q,v
async def d_s(d,c,t,w):
    global P
    r=d.to_list()
    o=len(r)
    if o==0:return d,0
    l(f"Processing {o:,} (t={t})")
    P=True
    p=atqdm(total=M,desc="Passes",position=0,leave=True)
    v=0
    q=r
    h=t
    for i in range(M):
        if i>0:h=max(h-R,50)
        z=B*(i+1)
        m=0
        l(f"Pass {i+1}/{M}: size {z}, t={h}%")
        p.update(1)
        s=min(z,len(q))
        c_n=(len(q)+s-1)//s
        y=atqdm(total=c_n,desc=f"P{i+1}",position=1,leave=True)
        g=[]
        k=0
        n=0
        for j in range(c_n):
            s_i=j*s
            e_i=min(s_i+s,len(q))
            a=q[s_i:e_i]
            b=len(a)
            u,m_i=await p_b_p(a,c,h,w)
            g.extend(u)
            k+=len(u)
            m+=m_i
            n+=b
            y.update(1)
            y.set_postfix({"k":f"{k}/{n}({k/n*100:.1f}%)","r":f"{m}","c":f"{n}/{len(q)}"})
            y.refresh()
        await y.close()
        q=g
        v+=m
        l(f"Pass {i+1}: {m} @ t={h}% (total: {v})")
        if m==0:
            l(f"No removals, skipping")
            p.update(M-i-1)
            break
    await p.close()
    P=False
    n=len(q)
    c=o-n
    r=(c/o*100)if o>0 else 0
    l(f"Done: {c:,} similar ({r:.1f}%)")
    return Dataset.from_list(q),c
async def f_d(s,d,c,t,w):
    try:
        u=S()
        ds,_=await l_s(s)
        if isinstance(ds,DatasetDict):
            fs=next(iter(ds.values()))
            if c not in fs.column_names:
                a=", ".join(fs.column_names)
                raise ValueError(f"'{c}' not found. Columns: {a}")
        else:
            if c not in ds.column_names:
                a=", ".join(ds.column_names)
                raise ValueError(f"'{c}' not found. Columns: {a}")
        l(f"Using col '{c}'")
        dd_r={}
        fd_r={}
        to=ta=tf=0
        for sn,sd in ds.items():
            l(f"Split '{sn}'...")
            oc=len(sd)
            to+=oc
            st=time.time()
            dd_ds,dr=dd(sd,c)
            dd_r[sn]=dd_ds
            dc=oc-dr
            ta+=dc
            e=time.time()-st
            r=oc/e if e>0 else 0
            l(f"Deduped '{sn}' in {e:.2f}s ({r:.1f}r/s):")
            l(f"- Orig: {oc:,}")
            l(f"- Deduped: {dc:,}")
            l(f"- Removed: {dr:,} ({dr/oc*100:.1f}%)")
            l(f"Sorting '{sn}' by len")
            dd_ds=s_b_l(dd_ds,c)
            st=time.time()
            fd_ds,sr=await d_s(dd_ds,c,t,w)
            fc=dc-sr
            tf+=fc
            e=time.time()-st
            r=dc/e if e>0 else 0
            l(f"Fuzzed '{sn}' in {e:.2f}s ({r:.1f}r/s):")
            l(f"- After dedup: {dc:,}")
            l(f"- After fuzz: {fc:,}")
            l(f"- Removed: {sr:,} ({sr/dc*100:.1f}%)")
            fd_r[sn]=fd_ds
            u.l_s(sn,oc,fc)
            if time.time()-u.l>30:
                l(u.g_s())
                u.l=time.time()
        dr=DatasetDict(dd_r)
        fr=DatasetDict(fd_r)
        dr.save_to_disk(d["deduped_dir"])
        l(f"Deduped saved to {d['deduped_dir']}")
        fr.save_to_disk(d["fuzzed_dir"])
        l(f"Fuzzed saved to {d['fuzzed_dir']}")
        dp=((to-ta)/to*100)if to>0 else 0
        fp=((ta-tf)/ta*100)if ta>0 else 0
        tr=((to-tf)/to*100)if to>0 else 0
        l("Summary:")
        l(f"- Orig: {to:,}")
        l(f"- After dedup: {ta:,} ({dp:.1f}%)")
        l(f"- Final: {tf:,} ({fp:.1f}%)")
        l(f"- Total reduction: {to-tf:,} ({tr:.1f}%)")
        l(u.g_s())
        return fr
    except Exception as e:
        l(f"Error: {e}")
        raise
async def u_d(d,x):
    try:
        l(f"Uploading to {x}...")
        d.push_to_hub(x)
        l(f"Upload success: {x}")
        return True
    except Exception as e:
        l(f"Upload error: {e}")
        return False
async def m():
    global c_l,f,d,B,W,T,R,M
    p=argparse.ArgumentParser(description="Deduplicate dataset",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--src",required=True,help="Source")
    p.add_argument("--dest",required=True,help="Destination")
    p.add_argument("--column",required=True,help="Column")
    p.add_argument("--threshold",type=float,default=80,help="Threshold")
    p.add_argument("--workers",type=int,default=W,help="Workers")
    p.add_argument("--threads",type=int,default=T,help="Threads")
    p.add_argument("--log-dir",default=L,help="Logs")
    p.add_argument("--output",default=os.getcwd(),help="Output")
    p.add_argument("--dry",action="store_true",help="Skip upload")
    p.add_argument("--batch-size",type=int,default=B,help="Batch")
    p.add_argument("--passes",type=int,default=M,help="Passes")
    p.add_argument("--threshold-reduction",type=int,default=R,help="Threshold drop")
    a=p.parse_args()
    if a.batch_size:B=a.batch_size
    if a.workers:W=a.workers
    if a.passes:M=a.passes
    if a.threads:T=a.threads
    if a.threshold_reduction is not None:R=a.threshold_reduction
    c_l,f=s_l(a.log_dir)
    d=s_d(a.log_dir,a.output)
    w=W
    c=multiprocessing.cpu_count()
    l(f"Config:")
    l(f"- ID: {d['run_id']}")
    l(f"- Src: {a.src}")
    l(f"- Dest: {a.dest}")
    l(f"- Col: {a.column}")
    l(f"- Threshold: {a.threshold}%")
    l(f"- Drop: {R}%")
    l(f"- CPUs: {c}")
    l(f"- Workers: {w}")
    l(f"- Threads: {T}")
    l(f"- Batch: {B}")
    l(f"- Passes: {M}")
    l(f"- Out: {a.output}")
    try:
        s=time.time()
        r=await f_d(a.src,a.dest,a.column,a.threshold,w)
        if not a.dry:
            u=await u_d(r,a.dest)
            if u:l(f"Success: {a.dest}")
            else:l(f"Upload failed: {d['fuzzed_dir']}")
        else:l(f"Dry run: {d['fuzzed_dir']}")
        e=time.time()-s
        l(f"Time: {e:.2f}s ({e/60:.2f}min)")
    except Exception as e:
        l(f"Error: {e}")
        return 1
    return 0
if __name__=="__main__":
    multiprocessing.freeze_support()
    if os.name=='nt':
        os.environ['PYTHONIOENCODING']='utf-8'
        multiprocessing.set_start_method('spawn')
    sys.exit(asyncio.run(m()))