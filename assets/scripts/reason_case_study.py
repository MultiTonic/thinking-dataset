import argparse as ap,os,asyncio,logging,time,requests,json
from datasets import load_dataset
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
async def v(c,sp):
    if not isinstance(c,dict):return False,"Not dict"
    ks=["endpoints","model","systems","prompts","splits"]
    for k in ks:
        if k not in c:return False,f"No {k}"
    if not isinstance(c["endpoints"],list) or len(c["endpoints"])==0:return False,"Need ≥1 endpoint"
    if not isinstance(c["splits"],dict):return False,"Splits must be dict"
    if sp not in c["splits"]:return False,f"No '{sp}' in splits"
    sc=c["splits"][sp]
    if not isinstance(c["systems"],dict) or sc not in c["systems"]:return False,f"No '{sc}' in systems"
    if not isinstance(c["prompts"],dict) or sc not in c["prompts"]:return False,f"No '{sc}' in prompts"
    return True,"Valid"
async def ld(src,sp):
    try:
        l(f"Loading dataset from {src}")
        d=load_dataset(src)
        if sp in d:
            l(f"Dataset loaded: {len(d[sp])} records in '{sp}' split")
            l(f"Dataset columns: {', '.join(d[sp].column_names)}")
        else:
            avail=", ".join(d.keys())
            l(f"Dataset loaded but split '{sp}' not found. Available splits: {avail}")
        return d
    except Exception as e:
        l(f"Error loading dataset: {e}")
        return None
async def sd(a):
    r=str(int(time.time()))
    o=os.path.abspath(a.output)
    ld=a.log_dir or os.path.join(o,"logs")
    d=os.path.join(o,"data")
    rd=os.path.join(d,r)
    cs=os.path.join(rd,"case_studies")
    t=os.path.join(rd,"temp")
    ck=os.path.join(rd,"checkpoints")
    for dr in[d,rd,cs,t,ck]:os.makedirs(dr,exist_ok=True)
    return{"r":r,"o":o,"l":ld,"d":d,"rd":rd,"cs":cs,"t":t,"ck":ck}
async def main(a):
    try:
        global dr
        dr=await sd(a)
        l(f"Config URL: {a.config}")
        l(f"Split: {a.split}")
        l(f"Output: {a.output}")
        l(f"Run ID: {dr['r']}")
        l(f"Data dir: {dr['d']}")
        c=await g(a.config)
        if not c:
            l("Failed to load config")
            return
        ok,m=await v(c,a.split)
        if not ok:
            l(f"Invalid configuration: {m}")
            return
        l("Config successfully loaded")
        sp=c["splits"][a.split]
        if a.src:
            l(f"Overriding source from '{c.get('src','')}' to '{a.src}'")
            c['src']=a.src
        src=c.get('src')
        if not src:
            l("No source dataset specified in config or arguments")
            return
        l(f"Source: {src}")
        l(f"Using split: {a.split} ({sp})")
        l(f"System prompt length: {len(c['systems'][sp])}")
        l(f"Prompt template length: {len(c['prompts'][sp])}")
        d=await ld(src,a.split)
        if not d:l("Failed to load dataset")
    except Exception as e:
        l(f"Fatal error: {str(e)}",True)
        raise e
if __name__=="__main__":
    if os.name=='nt':os.environ['PYTHONIOENCODING']='utf-8'
    p=ap.ArgumentParser()
    p.add_argument("--config",required=True,help="URL to the configuration file")
    p.add_argument("--src",help="Source dataset to load (overrides config)")
    p.add_argument("--log-dir",default=os.path.join(os.getcwd(),"logs"),help="Directory to save log files")
    p.add_argument("--split",required=True,help="Dataset split to process (e.g. english, chinese)")
    p.add_argument("--output",default=os.getcwd(),help="Output directory")
    a=p.parse_args()
    try:
        cl,f=s(a.log_dir)
        asyncio.run(main(a))
    except Exception as e:print(f"Fatal error: {e}");exit(1)
