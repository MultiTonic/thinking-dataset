import argparse as ap,os,asyncio as io,logging as lg,time as t,requests as rq
from openai import AsyncOpenAI as ai
from tenacity import retry,wait_random,stop_after_attempt as sa
from tqdm.asyncio import tqdm_asyncio as ta
from asyncio import TimeoutError
from datasets import load_dataset

G="https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw";T=3;D=.3;H="api.scaleway.ai"
def i(m:str,b:bool=True)->None:
    l.info(m)
    if b:c.info(m)
def log(p:str)->tuple[lg.Logger,lg.Logger]:
    os.makedirs(p,exist_ok=1)
    c=lg.getLogger("c");c.setLevel(lg.INFO);c.propagate=0
    h=lg.StreamHandler();h.setFormatter(lg.Formatter("[%(asctime)s] %(message)s","%X"));c.addHandler(h)
    f=lg.getLogger("f");f.setLevel(lg.INFO);f.propagate=0
    h=lg.FileHandler(os.path.join(p,f"cs_{str(int(t.time()))}.log"))
    h.setFormatter(lg.Formatter("[%(asctime)s] %(message)s","%X"));f.addHandler(h)
    return c,f
async def f():
    try:
        i(f"Fetching config from: {G}");r=rq.get(G)
        if r.status_code==200:
            j=r.json()
            i("Config fetched successfully")
            return{k:j[k]for k in['endpoints','model','source','dest','system_prompts','prompt_templates','max_tokens','temp']if k in j}
        i(f"Failed to fetch config: {r.status_code}",0);return None
    except Exception as e:i(f"Error fetching config: {e}",0);return None
@retry(stop=sa(T),wait=wait_random(min=.1,max=D),reraise=True)
async def x(s,m):
    async with m:
        try:
            t0=t.time()
            async with ai(base_url=f"https://{H}/{s['u']}/v1",api_key=s['k'])as o:
                try:
                    async with io.timeout(30):r=await o.chat.completions.create(model=d.get('model','deepseek-r1-distill-llama-70b'),messages=[{"role":"system","content":"Test message"},{"role":"user","content":"Respond with 'OK' if you can read this."}],max_tokens=10,temperature=0)
                except TimeoutError:l.info(f"Endpoint Fail! {s['n']}: 30.0s (Timeout)");return s['n'],30.0,None
                except Exception as e:l.info(f"Endpoint Fail! {s['n']}: API Error");raise
                e=round(t.time()-t0,2)
                if r and r.choices and r.choices[0].message:l.info(f"Endpoint OK! {s['n']}: {e}s");return s['n'],e,r.choices[0].message.content
                l.info(f"Endpoint Fail! {s['n']}: {e}s (No Response)");return s['n'],e,None
        except Exception as e:l.info(f"Endpoint Fail! {s['n']}: {str(e)}");raise
async def w():
    try:
        s=d.get('source')
        if not s:raise ValueError("No source dataset in config")
        ds=load_dataset(s,split="english")
        i(f"Dataset loaded successfully:")
        i(f"- source: {s}")
        i(f"- records: {len(ds)}")
        return ds
    except Exception as e:
        i(f"Error loading dataset '{s}': {e}",0)
        return None
async def m(a):
    try:
        r=str(int(t.time()))
        p=os.path.abspath(a.output);h=a.log_dir or os.path.join(p,"logs")
        dd=os.path.join(p,"data");cs=os.path.join(dd,"case_studies");tm=os.path.join(dd,"temp")
        [os.makedirs(x,exist_ok=1)for x in[dd,cs,tm]]
        g={"rid":r,"out":p,"log":h,"data":dd,"case_studies":cs,"temp":tm,"workers":a.workers or 5,"ends":len(d['endpoints'])}
        [i(x)for x in[f"Run ID: {g['rid']}",f"Output: {g['out']}",f"Log: {g['log']}",f"Data: {g['data']}",f"Cases: {g['case_studies']}",f"Temp: {g['temp']}",f"Workers: {g['workers']}",f"Endpoints: {g['ends']}"]]
        i(f"Config loaded:")
        [i(f"- {k}: {d[k]}")for k in['model','max_tokens','temperature']if k in d]
        if not isinstance(d,dict)or'endpoints'not in d:raise ValueError("Invalid config")
        s=io.Semaphore(g['workers']);i(f"Starting endpoint tests with {g['workers']} parallel workers")
        q=await ta.gather(*[x(e,s)for e in d["endpoints"]],desc="Test")
        c.info("Test results:")
        [c.info(f"- endpoint {st}! [ {n}: {tt}s ]")for n,tt,r in q if(st:="OK"if r=="OK"else"Fail")]
        c.info(f"- average time: {round(sum([tt for _,tt,_ in q if tt])/len([tt for _,tt,_ in q if tt]),2)}s")
        i("Loading dataset...")
        ds=await w()
        if not ds:raise ValueError("Failed to load dataset")
    except Exception as e:i(f"Fatal error: {str(e)}",1);raise e
if __name__=="__main__": 
    p=ap.ArgumentParser()
    [p.add_argument(a,**k)for a,k in[("--config",{"default":G}),("--output",{"default":os.getcwd()}),("--log-dir",{}),("--workers",{"type":int})]]
    a=p.parse_args();G=a.config
    try:
        p=os.path.join(os.getcwd(),"logs")
        global c,l
        c,l=log(a.log_dir or p)
        global d
        d=io.run(f())
        io.run(m(a))if d else c.error("No config")
    except Exception as e:
        c.error(f"F:{e}")
        exit(1)
