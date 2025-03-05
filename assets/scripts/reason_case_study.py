import argparse as ap,os,asyncio,logging,time,requests,random
from datasets import load_dataset
from openai import AsyncOpenAI
from tenacity import retry,wait_random,stop_after_attempt
from asyncio import TimeoutError
W=16;T=30;U="api.scaleway.ai";M=None
def l(m,c=True):
    try:
        f.info(m)
        if c:
            try:cl.info(m)
            except UnicodeEncodeError:cl.info(m.encode('ascii',errors='replace').decode('ascii'))
    except Exception as e:
        try:print(f"[LOGGING ERROR] Failed to log message: {str(e)}")
        except:pass
def s(p):
    os.makedirs(p,exist_ok=True);c,f=logging.getLogger("console"),logging.getLogger("file")
    h=logging.StreamHandler();h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    c.addHandler(h);c.setLevel(logging.INFO);c.propagate=False
    n=os.path.join(p,f"reason_{int(time.time())}.log")
    fh=logging.FileHandler(n,encoding='utf-8');fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    f.addHandler(fh);f.setLevel(logging.INFO);f.propagate=False;return c,f
async def g(u):
    try:
        l(f"Fetching config from: {u}");r=requests.get(u)
        if r.status_code==200:j=r.json();l("Config fetched successfully");return j
        l(f"Failed to fetch config: {r.status_code}",False);return None
    except Exception as e:l(f"Error fetching config: {e}",False);return None
async def v(c,p):
    if not isinstance(c,dict):return False,"Not dict"
    k=["endpoints","model","systems","prompts","splits","columns"]
    for i in k:
        if i not in c:return False,f"No {i}"
    if not isinstance(c["endpoints"],list) or len(c["endpoints"])==0:return False,"Need ≥1 endpoint"
    if not isinstance(c["splits"],dict):return False,"Splits must be dict"
    if not isinstance(c["columns"],dict):return False,"Columns must be dict"
    rc=["query","response","think"]
    for i in rc:
        if i not in c["columns"]:return False,f"Missing required column mapping: {i}"
    if p not in c["splits"]:return False,f"No '{p}' in splits"
    s=c["splits"][p]
    if not isinstance(c["systems"],dict) or s not in c["systems"]:return False,f"No '{s}' in systems"
    if not isinstance(c["prompts"],dict) or s not in c["prompts"]:return False,f"No '{s}' in prompts"
    return True,"Valid"
def ie(ec):
    e=[]
    for ep in ec:e.append({**ep,'last_call':0,'in_use':False})
    random.shuffle(e);return e
def gne(e):
    n=time.time();a=[]
    for i,ep in enumerate(e):
        if not ep['in_use'] and n-ep['last_call']>=12:a.append((i,ep))
    if not a:
        s=min(e,key=lambda x:x['last_call']+12 if not x['in_use'] else float('inf'))
        i=e.index(s);w=max(0,(s['last_call']+12)-n)
        if w>0:l(f"All endpoints busy or cooling down, will wait {w:.2f}s for next available");time.sleep(w)
        return i
    a.sort(key=lambda x:x[1]['last_call']);return a[0][0]
@retry(stop=stop_after_attempt(3),wait=wait_random(min=1,max=2),reraise=True)
async def te(ec,sm):
    async with sm:
        try:
            st=time.time();p=ec.get('p','unknown');n=ec.get('n','unknown')
            async with AsyncOpenAI(base_url=f"https://{U}/{ec['u']}/v1",api_key=ec['k']) as c:
                try:
                    async with asyncio.timeout(T):
                        r=await c.chat.completions.create(
                            model=M,
                            messages=[{"role":"system","content":"Test message"},{"role":"user","content":"Respond with 'OK' if you can read this."}],
                            max_tokens=10,temperature=0)
                except TimeoutError:
                    f.info(f"Endpoint Fail: {p}-{n}: {T}s (Timeout)")
                    return p,n,T,None
                except Exception as e:
                    em=str(e);f.info(f"Endpoint Fail: {p}-{n}: API Error - {em}")
                    if "429" in em or "TOO MANY TOKENS" in em or "rate limit" in em.lower():
                        l(f"Rate limit detected for endpoint {p}-{n}, considering it valid but busy")
                        await asyncio.sleep(3);return p,n,0.1,"RATE_LIMITED"
                    raise
                et=round(time.time()-st,2)
                if r and r.choices and r.choices[0].message:
                    f.info(f"Endpoint OK: {p}-{n}: {et}s")
                    return p,n,et,r.choices[0].message.content
                f.info(f"Endpoint Fail: {p}-{n}: {et}s (No Response)")
                return p,n,et,None
        except Exception as e:
            f.info(f"Endpoint Fail: {p}-{n}: {str(e)}");raise
async def te_all(wc):
    sm=asyncio.Semaphore(wc);l(f"Starting endpoint tests with {wc} parallel workers (timeout: {T}s)")
    tr=[];ts=[]
    for i,ep in enumerate(cc["endpoints"]):ts.append(te(ep,sm))
    rs=await asyncio.gather(*ts,return_exceptions=True)
    for i,r in enumerate(rs):
        ep=cc["endpoints"][i]
        if isinstance(r,Exception):
            l(f"Error testing endpoint {i+1}/{len(cc['endpoints'])}: {str(r)}")
            tr.append((ep.get('p','unknown'),ep.get('n','unknown'),0.0,None))
        else:
            p,n,tt,resp=r;io=resp=="OK" or resp=="RATE_LIMITED"
            st="OK" if resp=="OK" else "Rate Limited" if resp=="RATE_LIMITED" else "Failed"
            l(f"Tested endpoint {i+1}/{len(cc['endpoints'])}: {p}-{n} - {st}");tr.append(r)
    cl.info("Test results:")
    for p,n,tt,r in tr:
        if r=="RATE_LIMITED":s="Rate Limited";cl.info(f"- endpoint {s}! [ {p}-{n}: rate limited ]")
        else:s="OK" if r=="OK" else "Fail";cl.info(f"- endpoint {s}! [ {p}-{n}: {tt}s ]")
    t=[tt for _,_,tt,r in tr if r=="OK" and tt]
    if t:avg=round(sum(t)/len(t),2);cl.info(f"- average time: {avg}s")
    st={}
    for p,_,_,r in tr:
        if p not in st:st[p]={"total":0,"success":0}
        st[p]["total"]+=1
        if r=="OK" or r=="RATE_LIMITED":st[p]["success"]+=1
    cl.info("Provider summary:")
    for p,s in st.items():
        sr=(s["success"]/s["total"])*100 if s["total"]>0 else 0
        cl.info(f"- {p}: {s['success']}/{s['total']} endpoints ok ({sr:.1f}%)")
    return sum(1 for _,_,_,r in tr if r=="OK" or r=="RATE_LIMITED")
async def ld(s,p):
    try:
        l(f"Loading dataset from {s}");d=load_dataset(s)
        if p in d:
            l(f"Dataset loaded: {len(d[p])} records in '{p}' split")
            l(f"Dataset columns: {', '.join(d[p].column_names)}")
            return d
        else:
            a=", ".join(d.keys());l(f"Dataset loaded but split '{p}' not found. Available splits: {a}")
            return None
    except Exception as e:l(f"Error loading dataset: {e}");return None
async def sd(a):
    r=str(int(time.time()));o=os.path.abspath(a.output);ld=a.log_dir or os.path.join(o,"logs")
    d=os.path.join(o,"data");rd=os.path.join(d,r);cs=os.path.join(rd,"case_studies")
    t=os.path.join(rd,"temp");ck=os.path.join(rd,"checkpoints")
    for dr in[d,rd,cs,t,ck]:os.makedirs(dr,exist_ok=True)
    return{"r":r,"o":o,"l":ld,"d":d,"rd":rd,"cs":cs,"t":t,"ck":ck}
async def main(a):
    try:
        global dr,cc,eps,M;dr=await sd(a)
        l(f"Config URL: {a.config}");l(f"Split: {a.split}");l(f"Output: {a.output}")
        l(f"Run ID: {dr['r']}");l(f"Data dir: {dr['d']}");cc=await g(a.config)
        if not cc:l("Failed to load config");return
        k,m=await v(cc,a.split)
        if not k:l(f"Invalid configuration: {m}");return
        l("Config successfully loaded")
        M=a.model or cc["model"]
        l(f"Config loaded with {len(cc.get('endpoints',[]))} endpoints")
        l(f"- Model: {M}")
        l(f"- Testing timeout: {T}s")
        eps=ie(cc['endpoints'])
        w=a.workers if a.workers is not None else W
        wc=min(w,len(cc['endpoints']))
        if a.workers is not None and wc<a.workers:l(f"Capping workers from {a.workers} to {wc} based on available endpoints")
        re=await te_all(wc)
        if re==0:l("No working endpoints found.");return
        l(f"Found {re} working endpoints out of {len(cc['endpoints'])} total")
        s=cc["splits"][a.split]
        if a.src:l(f"Overriding source from '{cc.get('src','')}' to '{a.src}'");cc['src']=a.src
        src=cc.get('src')
        if not src:l("No source dataset specified in config or arguments");return
        l(f"Source: {src}");l(f"Using split: {a.split} ({s})")
        l(f"System prompt length: {len(cc['systems'][s])}");l(f"Prompt template length: {len(cc['prompts'][s])}")
        l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}")
        d=await ld(src,a.split)
        if not d:l("Failed to load dataset");return
        q=cc['columns']['query'];r=cc['columns']['response'];t=cc['columns']['think'];ds=d[a.split]
        if q not in ds.column_names:l(f"Error: Query column '{q}' not found in dataset");return
        if r not in ds.column_names:l(f"Error: Response column '{r}' not found in dataset");return
        l(f"Found {len(ds)} records with query and response columns")
    except Exception as e:l(f"Fatal error: {str(e)}",True);raise e
if __name__=="__main__":
    if os.name=='nt':os.environ['PYTHONIOENCODING']='utf-8'
    p=ap.ArgumentParser()
    p.add_argument("--config",required=True,help="URL to the configuration file")
    p.add_argument("--src",help="Source dataset to load (overrides config)")
    p.add_argument("--log-dir",default=os.path.join(os.getcwd(),"logs"),help="Directory to save log files")
    p.add_argument("--split",required=True,help="Dataset split to process (e.g. english, chinese)")
    p.add_argument("--output",default=os.getcwd(),help="Output directory")
    p.add_argument("--workers",type=int,help="Number of parallel workers for endpoint testing")
    p.add_argument("--model",help="Override model from config")
    a=p.parse_args()
    try:cl,f=s(a.log_dir);asyncio.run(main(a))
    except Exception as e:print(f"Fatal error: {e}");exit(1)
