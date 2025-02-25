import argparse as ap,os,asyncio as io,logging as lg,time as t,requests as rq
from openai import AsyncOpenAI as ai
from tenacity import retry,wait_random,stop_after_attempt as sa
from tqdm.asyncio import tqdm_asyncio as ta
from asyncio import TimeoutError
G="https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw";T=3;D=.3;H="api.scaleway.ai"
def log(p:str)->tuple[lg.Logger,lg.Logger]:
    os.makedirs(p,exist_ok=1)
    c=lg.getLogger("c");c.setLevel(lg.INFO);c.propagate=0
    h=lg.StreamHandler();h.setFormatter(lg.Formatter("[%(asctime)s] %(message)s","%X"));c.addHandler(h)
    f=lg.getLogger("f");f.setLevel(lg.INFO);f.propagate=0
    h=lg.FileHandler(os.path.join(p,f"cs_{str(int(t.time()))}.log"))
    h.setFormatter(lg.Formatter("%(asctime)s-%(message)s","%X"));f.addHandler(h)
    return c,f
async def f():
    try:
        c.info(f"Fetching config from: {G}");r=rq.get(G)
        if r.status_code==200:c.info("Config fetched successfully");return{k:r.json()[k]for k in['endpoints','model','system_prompts','prompt_templates']if k in r.json()}
        c.error(f"Failed to fetch config: {r.status_code}");return None
    except Exception as e:c.error(f"Error fetching config: {e}");return None
@retry(stop=sa(T),wait=wait_random(min=.1,max=D),reraise=True)
async def x(s,m):
    async with m:
        try:
            t0=t.time();l.info(f"Testing endpoint {s['n']}")
            async with ai(base_url=f"https://{H}/{s['u']}/v1",api_key=s['k'])as o:
                try:
                    async with io.timeout(30):r=await o.chat.completions.create(model=d.get('model','deepseek-r1-distill-llama-70b'),messages=[{"role":"system","content":"Test message"},{"role":"user","content":"Respond with 'OK' if you can read this."}],max_tokens=10,temperature=0)
                except TimeoutError:l.info(f"Timeout: {s['n']} after 30s");return s['n'],30.0,None
                except Exception as e:l.info(f"API Error: {s['n']} - {str(e)}");raise
                e=round(t.time()-t0,2)
                if r and r.choices and r.choices[0].message:l.info(f"Success: {s['n']} completed in {e}s");return s['n'],e,r.choices[0].message.content
                l.info(f"Failed: {s['n']} no valid response");return s['n'],e,None
        except Exception as e:l.info(f"Error: {s['n']} - {str(e)}");raise
async def m(a):
    try:
        p=os.path.abspath(a.output);h=a.log_dir or os.path.join(p,"logs")
        g={"out":p,"log":h,"workers":a.workers or 5,"ends":len(d['endpoints'])}
        [c.info(f"{m}")for m in["Configuration:",f"  Output: {g['out']}",f"  Logs: {g['log']}",f"  Workers: {g['workers']}",f"  Endpoints: {g['ends']}"]]
        if not isinstance(d,dict)or'endpoints'not in d:raise ValueError("Invalid config")
        s=io.Semaphore(g['workers']);c.info(f"Starting tests with {g['workers']} parallel workers")
        q=await ta.gather(*[x(e,s)for e in d["endpoints"]],desc="Test")
        c.info("Test Results")
        ts=int(t.time());[c.info(f"Endpoint {w}! {n}: {tt}s, last: {ts}")for n,tt,r in q if(w:="OK"if r=="OK"else"Fail")]
        v=[tt for _,tt,_ in q if tt];c.info(f"Average time: {round(sum(v)/len(v),2)}s")
    except Exception as e:c.info(f"Fatal error: {str(e)}");raise e
if __name__=="__main__": 
    p=ap.ArgumentParser();[p.add_argument(a,**k)for a,k in[("--config",{"default":G}),("--output",{"default":os.getcwd()}),("--log-dir",{}),("--workers",{"type":int})]];a=p.parse_args();G=a.config
    try:
        p=os.path.join(os.getcwd(),"logs")
        c,l=log(a.log_dir or p)
        d=io.run(f());io.run(m(a))if d else c.error("No config")
    except Exception as e:c.error(f"F:{e}");exit(1)
