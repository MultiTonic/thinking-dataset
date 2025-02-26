import argparse as ap,os,asyncio as io,logging as lg,time as t,requests as rq
from openai import AsyncOpenAI as ai
from tenacity import retry,wait_random,stop_after_attempt as sa
from tqdm.asyncio import tqdm_asyncio as ta
from asyncio import TimeoutError
from datasets import load_dataset, Dataset, DatasetDict
from huggingface_hub import HfApi
G="https://gist.githubusercontent.com/p3nGu1nZz/b8d661186cb71ff48f64cf338dedca9b/raw";T=3;D=.3;H="api.scaleway.ai"
def i(m:str,b:bool=1)->None:l.info(m);b and c.info(m)
def log(p:str)->tuple[lg.Logger,lg.Logger]:
    os.makedirs(p,exist_ok=1)
    c,f=lg.getLogger("c"),lg.getLogger("f")
    for l,h in[(c,lg.StreamHandler()),(f,lg.FileHandler(os.path.join(p,f"cs_{int(t.time())}.log")))]:l.setLevel(lg.INFO);l.propagate=0;h.setFormatter(lg.Formatter("[%(asctime)s] %(message)s","%X"));l.addHandler(h)
    return c,f
async def f():
    try:
        i(f"Fetching config from: {G}")
        r=rq.get(G)
        if r.status_code==200:
            j=r.json()
            i("Config fetched successfully")
            return{k:j[k]for k in['endpoints','model','src','dest','systems','prompts','max_tokens','tempurature']if k in j}
        i(f"Failed to fetch config: {r.status_code}",0)
        return None
    except Exception as e:i(f"Error fetching config: {e}",0);return None
@retry(stop=sa(T),wait=wait_random(min=.1,max=D),reraise=True)
async def x(s,m):
    async with m:
        try:
            t0=t.time()
            async with ai(base_url=f"https://{H}/{s['u']}/v1",api_key=s['k'])as o:
                try:
                    async with io.timeout(30):r=await o.chat.completions.create(
                        model=d.get('model','deepseek-r1-distill-llama-70b'),
                        messages=[{"role":"system","content":"Test message"},{"role":"user","content":"Respond with 'OK' if you can read this."}],
                        max_tokens=10,
                        temperature=0)
                except TimeoutError:l.info(f"Endpoint Fail: {s['p']}-{s['n']}: 30.0s (Timeout)");return s['n'],30.0,None
                except Exception:l.info(f"Endpoint Fail: {s['p']}-{s['n']}: API Error");raise
                e=round(t.time()-t0,2)
                if r and r.choices and r.choices[0].message:l.info(f"Endpoint OK: {s['p']}-{s['n']}: {e}s");return s['n'],e,r.choices[0].message.content
                l.info(f"Endpoint Fail: {s['p']}-{s['n']}: {e}s (No Response)");return s['n'],e,None
        except Exception as e:l.info(f"Endpoint Fail: {s['p']}-{s['n']}: {str(e)}");raise
async def w():
    try:
        s=d.get('src')
        if not s:raise ValueError("No source dataset in config")
        ds=load_dataset(s,split="english")
        tr,ts=len(ds),sum(len(r.get('stakeholders',{}).get('stakeholder',[]))for r in ds)
        i(f"Dataset loaded successfully:");i(f"- source: {s}");i(f"- total records: {tr}");i(f"- total stakeholders: {ts}");i(f"- total generations needed: {ts*2}");i(f"- average stakeholders per record: {ts/tr:.2f}")
        return ds
    except Exception as e:i(f"Error loading dataset '{s}': {e}",0);return None
async def u(p:list,d:str)->bool:
    try:
        i(f"Preparing to upload {len(p)} records to {d}")
        try:r=[{"case_study_info":"","prompt":x['prompts']['en']if'prompts'in x else"","original_info":x['case_study_info'],"endpoint":"","stakeholder":x.get('stakeholder',''),"motivation":x.get('motivation',''),"original_idx":x.get('original_idx',-1),"stakeholder_idx":x.get('stakeholder_idx',-1)}for x in p];i(f"Created {len(r)} base records")
        except Exception as e:i(f"Error creating base records: {str(e)}",0);raise
        try:ds=DatasetDict({'english':Dataset.from_list(r),'chinese':Dataset.from_list([{**x,'prompt':x['prompts'].get('zh','')}for x in r if'prompts'in x])});i(f"Created dataset dictionary - English: {len(ds['english'])}, Chinese: {len(ds['chinese'])}")
        except Exception as e:i(f"Error creating dataset dictionary: {str(e)}",0);raise
        try:ds.push_to_hub(d,private=1);i(f"Successfully pushed to hub: {d}")
        except Exception as e:i(f"Error pushing to hub: {str(e)}",0);raise
        i(f"Results uploaded to {d}:");i(f"- English records: {len(ds['english'])}");i(f"- Chinese records: {len(ds['chinese'])}");i(f"- Total prompts prepared: {len([x for x in r if x['prompt']])}")
        return 1
    except Exception as e:i(f"Error uploading results: {type(e).__name__}: {str(e)}",0);return 0
async def z(n:str)->bool:
    try:return bool(HfApi().dataset_info(n))
    except:return 0
async def prepare_prompt(c:str,s:str,m:str,l:str)->str:
    if not c or not s:return None
    system=d['systems'].get(l,"");prompt=d['prompts'].get(l,"")
    if not prompt or not system:i(f"No template/system found for language: {l}",0);return None
    return prompt.format(case_study_info=c.strip(),stakeholder=s.strip(),motivation=m.strip()or"Unknown motivations or intentions")
async def expand_dataset(ds)->list:
    expanded,skipped,valid,total,stakeholder_counts=[],0,0,len(ds),[]
    for idx,row in enumerate(ds):
        try:
            info=row.get('case_study_info','');stakeholders=row.get('stakeholders',{});stakeholder_list=stakeholders.get('stakeholder',[]);motivations=stakeholders.get('motivation',[])
            if stakeholder_list and motivations and len(stakeholder_list)==len(motivations):
                valid+=1;stakeholder_counts.append(len(stakeholder_list))
                for s_idx,(sh,mv)in enumerate(zip(stakeholder_list,motivations)):expanded.append({'case_study_info':info,'stakeholder':sh,'motivation':mv,'original_idx':idx,'stakeholder_idx':s_idx})
            else:skipped+=1;i(f"Skipping record {idx}: Invalid stakeholders structure",0)
        except Exception as ex:i(f"Error expanding record {idx}: {ex}",0);skipped+=1
    avg_stakeholders=sum(stakeholder_counts)/len(stakeholder_counts)if stakeholder_counts else 0;max_stakeholders=max(stakeholder_counts)if stakeholder_counts else 0
    i(f"Dataset expansion statistics:");i(f"- Original records: {total}");i(f"- Valid records: {valid}");i(f"- Skipped records: {skipped}");i(f"- Total stakeholders: {len(expanded)}");i(f"- Total generations needed: {len(expanded)*2}");i(f"- Average stakeholders per valid record: {avg_stakeholders:.2f}");i(f"- Max stakeholders in a record: {max_stakeholders}");i(f"- Success rate: {(valid/total*100):.1f}%")
    return expanded
async def prepare_all_prompts(records:list)->list:
    p,f,t=[],0,len(records)
    for r in records:
        try:
            e=await prepare_prompt(r['case_study_info'],r['stakeholder'],r['motivation'],'en')
            z=await prepare_prompt(r['case_study_info'],r['stakeholder'],r['motivation'],'zh')
            if e and z:p.append({**r,'prompts':{'en':e,'zh':z}})
            else:f+=1
        except Exception as e:i(f"Error preparing prompts for record: {e}",0);f+=1
    i(f"Prompt preparation statistics:");i(f"- Total records processed: {t}");i(f"- Successfully prepared: {len(p)}");i(f"- Total prompts prepared: {len(p)*2}");i(f"- Failed preparations: {f}");i(f"- Success rate: {(len(p)/t*100):.1f}%")
    return p
async def m(a):
    try:
        r=str(int(t.time()));p=os.path.abspath(a.output);h=a.log_dir or os.path.join(p,"logs");dd,cs,tm=[os.path.join(p,x)for x in["data","data/case_studies","data/temp"]];[os.makedirs(x,exist_ok=1)for x in[dd,cs,tm]];g={"rid":r,"out":p,"log":h,"data":dd,"case_studies":cs,"temp":tm,"workers":a.workers or 5,"ends":len(d['endpoints'])};[i(x)for x in[f"Run ID: {g['rid']}",f"Output: {g['out']}",f"Log: {g['log']}",f"Data: {g['data']}",f"Cases: {g['case_studies']}",f"Temp: {g['temp']}",f"Workers: {g['workers']}",f"Endpoints: {g['ends']}"]]
        required_keys=['model','max_tokens','tempurature','systems','prompts'];missing_keys=[k for k in required_keys if k not in d]
        if missing_keys:raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")
        i(f"Config loaded:");[i(f"- {k}: {d[k]}")for k in['model','max_tokens','tempurature']if k in d]
        if not isinstance(d,dict)or'endpoints'not in d:raise ValueError("Invalid config")
        s=io.Semaphore(g['workers']);i(f"Starting endpoint tests with {g['workers']} parallel workers");q=await ta.gather(*[x(e,s)for e in d["endpoints"]],desc="Test")
        c.info("Test results:");[c.info(f"- endpoint {st}! [ {n}: {tt}s ]")for n,tt,r in q if(st:="OK"if r=="OK"else"Fail")];c.info(f"- average time: {round(sum([tt for _,tt,_ in q if tt])/len([tt for _,tt,_ in q if tt]),2)}s")
        i("Loading dataset...");ds=await w()
        if not ds:raise ValueError("Failed to load dataset")
        i("Expanding dataset records...");expanded=await expand_dataset(ds)
        i("Preparing prompts...");prepared=await prepare_all_prompts(expanded)
        dest=d.get('dest')
        if not dest:raise ValueError("No destination dataset in config")
        if not await u(prepared,dest):raise ValueError("Failed to upload initial dataset")
        i(f"Successfully initialized dataset structure at {dest}")
    except Exception as e:i(f"Fatal error: {str(e)}",1);raise e
if __name__=="__main__":
    p=ap.ArgumentParser();[p.add_argument(a,**k)for a,k in[("--config",{"default":G}),("--output",{"default":os.getcwd()}),("--log-dir",{}),("--workers",{"type":int})]];a=p.parse_args();G=a.config
    try:
        global c,l,d;c,l=log(a.log_dir or os.path.join(os.getcwd(),"logs"));d=io.run(f());io.run(m(a))if d else c.error("No config")
    except Exception as e:c.error(f"F:{e}");exit(1)