# flake8: noqa
import argparse as ap,os,asyncio as io,logging as lg,time as t,random as r,aiohttp as ah,requests
from openai import AsyncOpenAI as ai
from tenacity import retry,wait_random,stop_after_attempt
from tqdm.asyncio import tqdm_asyncio
GU="https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw";TR=3;DL=0.9;HA="api.scaleway.ai"
async def _f():
    try:
        r=requests.get(GU)
        if r.status_code!=200:raise Exception(f"HTTP {r.status_code}")
        d=r.json()
        if not all(k in d for k in["endpoints","model","messages"]):raise Exception("Missing required fields")
        return d
    except requests.RequestException as e:raise Exception(f"Network error: {e}")
    except ValueError as e:raise Exception(f"Invalid JSON: {e}")
    except Exception as e:raise Exception(f"Config error: {e}")
n=str(int(t.time()))
fl=lg.getLogger("file");fl.setLevel(lg.INFO);fl.propagate=False
cl=lg.getLogger("console");cl.setLevel(lg.INFO);cl.addHandler(lg.StreamHandler())
@retry(stop=stop_after_attempt(TR),wait=wait_random(min=0.1,max=DL))
async def _t(s,sem):
    async with sem:
        try:
            t0=t.time()
            async with ai(base_url=f"https://{HA}/{s['u']}/v1",api_key=s['k'])as o:
                r=await o.chat.completions.create(model=c["model"],messages=c["messages"],
                    max_tokens=c.get("max_tokens",4096),temperature=c.get("temperature",1))
                rt=round(t.time()-t0,2)
                fl.info(f"OK:{s['n']} [{rt}s]");return s['n'],rt
        except Exception as x:fl.info(f"Err:{s['n']}:{x}");return s['n'],None
async def _m(a):
    try:
        b=os.path.abspath(a.output);h=a.log_dir or os.path.join(b,"logs")
        os.makedirs(b,exist_ok=True);os.makedirs(h,exist_ok=True);os.makedirs(os.path.join(b,"data"),exist_ok=True)
        f=lg.FileHandler(os.path.join(h,f"case_study_{n}.log"));f.setFormatter(lg.Formatter("%(asctime)s - %(message)s","%X"));fl.addHandler(f)
        sem=io.Semaphore(a.workers or 5)
        cfg=dict(run=n,model=c["model"],workers=a.workers or 5,msgs=len(c["messages"]),eps=len(c["endpoints"]),
            temp=c.get("temperature",0.6),max_tok=c.get("max_tokens",1))
        fl.info(f"Cfg:{cfg}")
        cl.info("CFG = {"+", ".join(f"{k}:{v}"for k,v in cfg.items())+"}")
        r=await tqdm_asyncio.gather(*[_t(s,sem)for s in c["endpoints"]],desc="Testing endpoints")
        times=[t for _,t in r if t]
        avg=round(sum(times)/len(times),2)if times else 0
        fl.info("Results:"+str(r))
        fl.info(f"Stats: avg={avg}s")
    except Exception as x:fl.info(f"Error:{x}");raise x
if __name__=="__main__": 
    p=ap.ArgumentParser(description="Scaleway AI Endpoints Tester")
    p.add_argument("--config",default=GU,help="Config gist URL. ex: %(default)s")
    p.add_argument("--output",default=os.getcwd(),help="Base output directory. ex: /path/to/output")
    p.add_argument("--log-dir",help="Custom logs directory. ex: /path/to/logs")
    p.add_argument("--workers",type=int,help="Number of concurrent workers. ex: 5")
    a=p.parse_args();GU=a.config
    try:
        cl.info(f"Fetching config from {GU}")
        c=io.run(_f())
        io.run(_m(a))
    except Exception as e:cl.error(f"Failed: {e}");exit(1)
