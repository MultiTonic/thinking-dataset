import argparse as ap,os,asyncio,logging,time,requests,random   
from tenacity import retry,wait_random,stop_after_attempt
from datasets import load_dataset,Dataset,DatasetDict
from asyncio import TimeoutError
from openai import AsyncOpenAI
from ollama import AsyncClient

W=16;T=30
def l(m,c=True):
    if fl and not test_mode:fl.info(m)
    if c and cl:
        try:cl.info(m)
        except UnicodeEncodeError:cl.info(m.encode('ascii',errors='replace').decode('ascii'))
def s(p,tm=False):
    if tm:
        c=logging.getLogger("console")
        h=logging.StreamHandler();h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
        c.addHandler(h);c.setLevel(logging.INFO);c.propagate=False
        return c,None
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
        l(f"Failed to fetch config: {r.status_code}");return None
    except Exception as e:l(f"Error fetching config: {e}");return None
async def v(c,p=None):
    if not isinstance(c,dict):return False,"Not dict"
    k=["endpoints"]
    for i in k:
        if i not in c:return False,f"No {i}"
    if not isinstance(c["endpoints"],list) or len(c["endpoints"])==0:return False,"Need ≥1 endpoint"
    if p is None:return True,"Valid for test mode"
    if "splits" not in c:return False,"No splits"
    if "systems" not in c:return False,"No systems"
    if "prompts" not in c:return False,"No prompts"
    if "columns" not in c:return False,"No columns"
    if not isinstance(c["splits"],dict):return False,"Splits must be dict"
    if not isinstance(c["columns"],dict):return False,"Columns must be dict"
    rc=["query","response","think"]
    for i in rc:
        if i not in c["columns"]:return False,f"Missing required column mapping: {i}"
    if p not in c["splits"]:return False,f"No '{p}' in splits"
    s=c["splits"][p]
    if not isinstance(c["systems"],dict) or s not in c["systems"]:return False,f"No '{s}' in systems"
    if not isinstance(c["prompts"],dict) or s not in c["prompts"]:return False,f"No '{s}' in prompts"
    for ep in c["endpoints"]:
        if "m" not in ep:return False,f"Endpoint {ep.get('n','unknown')} missing model"
    return True,"Valid"
def ie(ec):
    e=[];[e.append({**ep,'last_call':0,'in_use':False}) for ep in ec];random.shuffle(e);return e
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
async def ld(s,p,o=0,m=0):
    try:
        l(f"Loading dataset from {s}");d=load_dataset(s)
        if p in d:
            full=d[p];total=len(full)
            if o>0 or m>0:
                if o>=total:
                    l(f"Error: Offset {o} exceeds dataset size {total}");return None
                end=total if m==0 else min(o+m,total)
                ds=full.select(range(o,end))
                l(f"Using dataset slice: records {o} to {end-1} (out of {total} total)")
            else:
                ds=full;l(f"Using complete dataset: {total} records")
            l(f"Dataset loaded: {len(ds)} records in '{p}' split")
            l(f"Dataset columns: {', '.join(ds.column_names)}")
            return ds
        else:
            a=", ".join(d.keys());l(f"Dataset loaded but split '{p}' not found. Available splits: {a}")
            return None
    except Exception as e:l(f"Error loading dataset: {e}");return None
async def ld_all(s,sps,o=0,m=0):
    d={}
    for sp in sps:d[sp]=await ld(s,sp,o,m)
    return d
async def p_pmt(q,r):
    return f"Thinking process for query: {q[:50]}..."
async def proc_1sp(sp,s,src,o,m,dr):
    l(f"Processing split: {sp} ({s})")
    l(f"System prompt length: {len(cc['systems'][s])}");l(f"Prompt template length: {len(cc['prompts'][s])}")
    l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}")
    d=await ld(src,sp,o,m)
    if not d:l(f"Failed to load dataset for split {sp}");return {},0
    q=cc['columns']['query'];r=cc['columns']['response'];t=cc['columns']['think']
    if q not in d.column_names:l(f"Error: Query column '{q}' not found in dataset");return {},0
    if r not in d.column_names:l(f"Error: Response column '{r}' not found in dataset");return {},0
    l(f"Found {len(d)} records with query and response columns for split {sp}")
    l(f"Preparing {len(d)} prompts for split {sp}")
    pm=[]
    for row in d:pm.append(await p_pmt(row[q],row[r]))
    l(f"Prepared {len(pm)} prompts for split {sp}")
    l(f"Mock generating responses for {len(d)} records")
    rs=[]
    for i,row in enumerate(d):
        rd={}
        if "id" in row:rd["id"]=row["id"]
        rd[r]=row[r]
        rd[t]=f"Mock thinking process for record {i+1}"
        rd[q]=row[q]
        for c in row:
            if c not in rd and c not in[r,t,q]:rd[c]=row[c]
        rs.append(rd)
    l(f"Prepared {len(rs)} records with column order: response, {t}, {q}, [other fields]")
    ds=Dataset.from_list(rs)
    spd=os.path.join(dr["cs"],sp)
    os.makedirs(spd,exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved {len(rs)} records to local directory: {spd}")
    return {sp:ds},len(rs)
async def proc_sp(sp,s,src,o,m,dr,all_ds,total_recs):
    l(f"Processing split: {sp} ({s})")
    l(f"System prompt length: {len(cc['systems'][s])}");l(f"Prompt template length: {len(cc['prompts'][s])}")
    l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}")
    d=await ld(src,sp,o,m)
    if not d:l(f"Failed to load dataset for split {sp}");return all_ds,total_recs
    q=cc['columns']['query'];r=cc['columns']['response'];t=cc['columns']['think'];
    if q not in d.column_names:l(f"Error: Query column '{q}' not found in dataset");return all_ds,total_recs
    if r not in d.column_names:l(f"Error: Response column '{r}' not found in dataset");return all_ds,total_recs
    l(f"Found {len(d)} records with query and response columns for split {sp}")
    rs=[]
    for _,s in enumerate(d):
        rd={}
        for k in ("id",):
            if k in s:rd[k]=s[k]
        rd[r]=s[r]
        rd[t]=s.get(t,"")
        rd[q]=s[q]
        for c in s:
            if c not in rd and c not in[r,t,q]:rd[c]=s[c]
        rs.append(rd)
    l(f"Prepared {len(rs)} records with column order: response, {t}, {q}, [other fields]")
    ds=Dataset.from_list(rs)
    spd=os.path.join(dr["cs"],sp)
    os.makedirs(spd,exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved {len(rs)} records to local directory: {spd}")
    all_ds[sp]=ds
    total_recs+=len(rs)
    return all_ds,total_recs
async def proc_split(sp,s,src,o,m,dr,all_ds,tot):
    l(f"Processing split: {sp} ({s})")
    l(f"System prompt length: {len(cc['systems'][s])}")
    l(f"Prompt template length: {len(cc['prompts'][s])}")
    l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}")
    d=await ld(src,sp,o,m)
    if not d:l(f"Failed to load dataset for split {sp}");return all_ds,tot
    q=cc['columns']['query'];r=cc['columns']['response'];t=cc['columns']['think']
    if q not in d.column_names:l(f"Error: Query column '{q}' not found in dataset");return all_ds,tot
    if r not in d.column_names:l(f"Error: Response column '{r}' not found in dataset");return all_ds,tot
    l(f"Found {len(d)} records with query and response columns for split {sp}")
    l(f"Preparing {len(d)} prompts for split {sp}")
    pm=[]
    for row in d:pm.append(await p_pmt(row[q],row[r]))
    l(f"Prepared {len(pm)} prompts for split {sp}")
    l(f"Mock generating responses for {len(d)} records")
    rs=[]
    for i,row in enumerate(d):
        rd={}
        if "id" in row:rd["id"]=row["id"]
        rd[r]=row[r]
        rd[t]=f"Mock thinking process for record {i+1}"
        rd[q]=row[q]
        for c in row:
            if c not in rd and c not in [r,t,q]:rd[c]=row[c]
        rs.append(rd)
    l(f"Prepared {len(rs)} records with column order: response, {t}, {q}, [other fields]")
    ds=Dataset.from_list(rs)
    spd=os.path.join(dr["cs"],sp)
    os.makedirs(spd,exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved {len(rs)} records to local directory: {spd}")
    all_ds[sp]=ds
    tot+=len(rs)
    return all_ds,tot
async def setup_dirs(a):
    r=str(int(time.time()));o=os.path.abspath(a.output);logdir=a.log_dir or os.path.join(o,"logs")
    d=os.path.join(o,"data");rd=os.path.join(d,r);cs=os.path.join(rd,"case_study")
    t=os.path.join(rd,"temp");ck=os.path.join(rd,"checkpoints")
    for dr in[d,rd,cs,t,ck]:os.makedirs(dr,exist_ok=True)
    return{"r":r,"o":o,"l":logdir,"d":d,"rd":rd,"cs":cs,"t":t,"ck":ck}
async def tc_openai(ec,msg,_):
    async with AsyncOpenAI(base_url=ec['u'],api_key=ec.get('k','')) as c:return await c.chat.completions.create(
        model=ec['m'],messages=msg,max_tokens=10,temperature=0,stream=False)
async def tc_ollama(ec,msg,_):
    c=AsyncClient(host=ec['u']);return await c.chat(model=ec['m'],messages=msg,stream=False,
        options={"temperature":0,"num_predict":10,"num_ctx":4096})
@retry(stop=stop_after_attempt(3),wait=wait_random(min=1,max=2),reraise=True)
async def te(ec,sm):
    async with sm:
        try:
            st=time.time();p=ec.get('p','unknown');n=ec.get('n','unknown')
            prov=ec.get('p','').lower()
            msg=[{"role":"system","content":"Test message"},{"role":"user","content":"Respond with 'OK' if you can read this."}]
            try:
                async with asyncio.timeout(T):
                    if prov=="openai":r=await tc_openai(ec,msg,None)
                    elif prov=="ollama":r=await tc_ollama(ec,msg,None)
                    else:l(f"Unknown provider type: {prov}");return p,n,0.0,None
            except TimeoutError:
                if not test_mode and fl:fl.info(f"Endpoint Fail: {p}-{n}: {T}s (Timeout)")
                return p,n,T,None
            except Exception as e:
                em=str(e)
                if not test_mode and fl:fl.info(f"Endpoint Fail: {p}-{n}: API Error - {em}")
                if "429" in em or "TOO MANY TOKENS" in em or "rate limit" in em.lower():
                    l(f"Rate limit detected for endpoint {p}-{n}, considering it valid but busy")
                    await asyncio.sleep(3);return p,n,0.1,"RATE_LIMITED"
                raise
            et=round(time.time()-st,2)
            if prov=="openai" and r and r.choices and r.choices[0].message:
                if not test_mode and fl:fl.info(f"Endpoint OK: {p}-{n}: {et}s")
                return p,n,et,r.choices[0].message.content
            elif prov=="ollama" and r and r.message and r.message.content:
                if not test_mode and fl:fl.info(f"Endpoint OK: {p}-{n}: {et}s")
                return p,n,et,r.message.content
            if not test_mode and fl:fl.info(f"Endpoint Fail: {p}-{n}: {et}s (No Response)")
            return p,n,et,None
        except Exception as e:
            if not test_mode and fl:fl.info(f"Endpoint Fail: {p}-{n}: {str(e)}")
            raise
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
async def push_to_hub(data,split,dst):
    try:
        l(f"Preparing to push data to {dst}")
        try:
            existing=DatasetDict.load_from_hub(dst)
            l(f"Loaded existing dataset with splits: {', '.join(existing.keys())}")
            existing[split]=data;dd=existing
        except:dd=DatasetDict({split:data})
        hft=cc.get('hf_token');prv=cc.get('private',False)
        l("Using HF_TOKEN from config");dd.push_to_hub(dst,token=hft,private=prv)
        l(f"Successfully pushed to hub: {dst}")
        return True
    except Exception as e:l(f"Error pushing to hub: {str(e)}",True);return False
async def main(a):
    try:
        global dr,cc,eps,test_mode
        test_mode=a.test
        dr=await setup_dirs(a) if not test_mode else {}
        if not test_mode:l(f"Run ID: {dr['r']}");l(f"Data dir: {dr['d']}")
        l(f"Config URL: {a.config}")
        cc=await g(a.config)
        if not cc:l("Failed to load config");return
        k,m=await v(cc,None)
        if not k:l(f"Invalid configuration: {m}");return
        l("Config successfully loaded")
        l(f"Config loaded with {len(cc.get('endpoints',[]))} endpoints")
        l(f"- Testing timeout: {T}s")
        eps=ie(cc['endpoints'])
        w=a.workers if a.workers is not None else W
        wc=min(w,len(cc['endpoints']))
        if a.workers is not None and wc<a.workers:l(f"Capping workers from {a.workers} to {wc} based on available endpoints")
        re=await te_all(wc)
        if re==0:l("No working endpoints found.");return
        l(f"Found {re} working endpoints out of {len(cc['endpoints'])} total")
        if test_mode:l("Test completed successfully.");return
        if a.src:l(f"Overriding source from '{cc.get('src','')}' to '{a.src}'");cc['src']=a.src
        src=cc.get('src')
        if not src:l("No source dataset specified in config or arguments");return
        dst=a.dst or cc.get('dst')
        if not dst:l("No destination dataset specified in config or arguments");return
        sps=list(cc["splits"].keys()) if hasattr(cc["splits"],"keys") else []
        if not sps:l("No splits found in config");return
        l(f"Found {len(sps)} splits in config: {', '.join(sps)}")
        all_ds={};tot=0
        for sp in sps:
            s=cc["splits"][sp]
            ds,cnt=await proc_1sp(sp,s,src,a.offset,a.max_records,dr)
            if ds:all_ds.update(ds);tot+=cnt
        if all_ds:
            l(f"TELEMETRY: Final dataset preparation started")
            dd=DatasetDict(all_ds)
            l(f"Created dataset dictionary with {tot} total records across {len(all_ds)} splits")
            for sn,sd in dd.items():
                l(f"- Split '{sn}': {len(sd)} records, columns: {', '.join(sd.column_names)}")
            l(f"Average records per split: {tot/len(all_ds):.1f}")
            dd.save_to_disk(dr["cs"])
            l(f"Saved unified dataset to {dr['cs']}")
            l(f"Preparing to push unified dataset to {dst}")
            hft=cc.get('hf_token');prv=cc.get('private',True)
            l("Using HF_TOKEN from config")
            dd.push_to_hub(dst,token=hft,private=prv)
            l(f"Successfully pushed unified dataset with {len(all_ds)} splits to hub: {dst}")
        else:l("No data processed, skipping push to hub")
        l(f"Finished processing all splits")
    except Exception as e:l(f"Fatal error: {str(e)}");raise e
if __name__=="__main__": 
    if os.name=='nt':os.environ['PYTHONIOENCODING']='utf-8'
    p=ap.ArgumentParser()
    p.add_argument("--config",required=True,help="URL to the configuration file")
    p.add_argument("--test",action="store_true",help="Only test endpoints and exit")
    p.add_argument("--src",help="Source dataset to load (overrides config)")
    p.add_argument("--dst",help="Destination dataset to push to (overrides config)")
    p.add_argument("--log-dir",default=os.path.join(os.getcwd(),"logs"),help="Directory to save log files")
    p.add_argument("--output",default=os.getcwd(),help="Output directory")
    p.add_argument("--workers",type=int,help="Number of parallel workers for endpoint testing")
    p.add_argument("--offset",type=int,default=0,help="Offset to start processing records from")
    p.add_argument("--max-records",type=int,default=0,help="Maximum number of records to process per split")
    a=p.parse_args()
    global test_mode,cl,fl;test_mode=a.test
    try:cl,fl=s(a.log_dir,test_mode);asyncio.run(main(a))
    except Exception as e:print(f"Fatal error: {e}");exit(1)