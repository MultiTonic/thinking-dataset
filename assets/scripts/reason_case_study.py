import argparse as ap,os,asyncio,logging,time,requests,json
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
    os.makedirs(p,exist_ok=True)
    c,f=logging.getLogger("console"),logging.getLogger("file")
    h=logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    c.addHandler(h);c.setLevel(logging.INFO);c.propagate=False
    n=os.path.join(p,f"r_{int(time.time())}.log")
    fh=logging.FileHandler(n,encoding='utf-8')
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s","%X"))
    f.addHandler(fh);f.setLevel(logging.INFO);f.propagate=False
    return c,f
async def g(u):
    try:
        l(f"Fetching config from: {u}")
        r=requests.get(u)
        if r.status_code==200:
            j=r.json()
            l("Config fetched successfully")
            return j
        l(f"Failed to fetch config: {r.status_code}",False)
        return None
    except Exception as e:
        l(f"Error fetching config: {e}",False)
        return None
async def v(c,lng):
    if not isinstance(c,dict):return False,"Not dict"
    ks=["endpoints","model","systems","prompts"]
    for k in ks:
        if k not in c:return False,f"No {k}"
    if not isinstance(c["endpoints"],list) or len(c["endpoints"])==0:return False,"Need ≥1 endpoint"
    for k in ["systems","prompts"]:
        if not isinstance(c[k],dict) or len(c[k])==0:return False,f"Need ≥1 {k}"
    if lng not in c["systems"]:return False,f"No '{lng}' in systems"
    if lng not in c["prompts"]:return False,f"No '{lng}' in prompts"
    return True,"Valid"
async def main(a):
    try:
        l(f"Config URL: {a.config}")
        l(f"Language: {a.lang}")
        l(f"Output: {a.output}")
        c=await g(a.config)
        if c:
            ok,m=await v(c,a.lang)
            if not ok:
                l(f"Invalid configuration: {m}")
                return
            l("Config successfully loaded")
            l(f"Using language: {a.lang}")
            l(f"System prompt length: {len(c['systems'][a.lang])}")
            l(f"Prompt template length: {len(c['prompts'][a.lang])}")
        else:l("Failed to load config")
    except Exception as e:
        l(f"Fatal error: {str(e)}",True)
        raise e
if __name__=="__main__":
    if os.name=='nt':os.environ['PYTHONIOENCODING']='utf-8'
    p=ap.ArgumentParser()
    p.add_argument("--config",required=True,help="URL to the configuration file")
    p.add_argument("--log-dir",default=os.path.join(os.getcwd(),"logs"),help="Directory to save log files")
    p.add_argument("--lang",required=True,choices=["en","zh"],help="Language to use (en/zh)")
    p.add_argument("--output",default=os.getcwd(),help="Output directory")
    a=p.parse_args()
    try:
        cl,f=s(a.log_dir)
        asyncio.run(main(a))
    except Exception as e:print(f"Fatal error: {e}");exit(1)
