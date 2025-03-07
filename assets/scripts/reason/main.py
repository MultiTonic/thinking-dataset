import argparse as ap,os,asyncio,logging,time,requests,random,json
from tenacity import retry,wait_random,stop_after_attempt, retry_if_exception_type
from datasets import load_dataset,Dataset,DatasetDict
from asyncio import TimeoutError
from openai import AsyncOpenAI
from ollama import AsyncClient
import traceback

W=16;T=30;C=100;B=100;R=10;RT=600;EC=12

class TelemetryStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.processed_records = set()

    def log_success(self, record_id, language):
        self.total_attempts += 1
        unique_id = f"{language}_{record_id}"
        if unique_id not in self.processed_records:
            self.successful_generations += 1
            self.processed_records.add(unique_id)
    
    def log_failure(self, record_id, language, error_type):
        self.total_attempts += 1
        self.failed_generations += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def reset_stats(self):
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.processed_records = set()
    
    def get_telemetry_string(self, total_needed):
        elapsed = time.time() - self.start_time
        remaining = total_needed - self.successful_generations
        rpm = (self.total_attempts / elapsed * 60) if elapsed > 0 else 0
        error_rate = (self.failed_generations / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        if rpm > 0:
            est_minutes = remaining / (rpm * (1 - error_rate/100)) if error_rate < 100 else float('inf')
            time_remaining = f"{est_minutes:.1f} min" if est_minutes < 60 else f"{est_minutes/60:.1f} hours"
        else:
            time_remaining = "unknown"
            
        return (f"TELEMETRY: {self.successful_generations}/{total_needed} complete ({self.successful_generations/total_needed*100:.1f}%) • "
                f"{remaining} remaining • {rpm:.1f} req/min • "
                f"{error_rate:.1f}% errors • Est. remaining: {time_remaining}")

def check_min_length(response_text: str, min_length: int):
    if min_length and len(response_text) < min_length:
        raise ValueError(f"Response length {len(response_text)} is shorter than minimum required length {min_length}")
    return True

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
    if"endpoints"not in c:return False,"No endpoints"
    if not isinstance(c["endpoints"],list)or len(c["endpoints"])==0:return False,"Need ≥1 endpoint"
    for e in c["endpoints"]:
        if"m"not in e:return False,f"Endpoint {e.get('n','unknown')} missing model"
    for p_name in["temperature","max_tokens","min_length"]:
        if p_name not in c:return False,f"No {p_name}"
        if not isinstance(c[p_name],int):return False,f"{p_name} must be an integer"
    for p_name in["src","dst","hf_token"]:
        if p_name in c and not isinstance(c[p_name],str):return False,f"{p_name} must be a string"
    if"private"in c and not isinstance(c["private"],bool):return False,"private must be a boolean"
    if p is None:return True,"Valid for test mode"
    for k in["splits","systems","metacogs","columns"]:
        if k not in c:return False,f"No {k}"
        if not isinstance(c[k],dict):return False,f"{k} must be dict"
    for col in["query","response","think"]:
        if col not in c["columns"]:return False,f"Missing required column mapping: {col}"
    if p not in c["splits"]:return False,f"No '{p}' in splits"
    
    system_categories = ["dark_thoughts", "benign"]
    found_in_systems = False
    for category in system_categories:
        if category in c["systems"] and p in c["systems"][category]:
            found_in_systems = True
            break
    if not found_in_systems:return False,f"No '{p}' in systems categories"
    
    found_in_metacogs = False
    for category in system_categories:
        if category in c["metacogs"] and p in c["metacogs"][category]:
            found_in_metacogs = True
            break
    if not found_in_metacogs:return False,f"No '{p}' in metacogs categories"
    
    return True,"Valid"
def ie(ec):
    e=[];[e.append({**ep,'last_call':0,'in_use':False}) for ep in ec];random.shuffle(e);return e
def gne(e):
    n=time.time()
    a=[]
    for i,ep in enumerate(e):
        provider = ep.get('p', '').lower()
        if not ep['in_use'] and (provider == "ollama" or n-ep['last_call']>=EC):
            a.append((i,ep))
    
    if not a:
        s=min(e, key=lambda x: x['last_call'] if x.get('p','').lower() == "ollama" else (
            x['last_call']+EC if not x['in_use'] else float('inf')))
        i=e.index(s)
        
        if s.get('p','').lower() != "ollama":
            w=max(0,(s['last_call']+EC)-n)
            if w>0:
                l(f"All endpoints busy or cooling down, will wait {w:.2f}s for next available")
                time.sleep(w)
        return i
    
    a.sort(key=lambda x:x[1]['last_call'])
    return a[0][0]
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
def ie(ec):
    e=[];[e.append({**ep,'last_call':0,'in_use':False}) for ep in ec];random.shuffle(e);return e

async def proc_1sp(sp,s,src,o,m,dr):
    global telemetry_stats
    telemetry_stats.reset_stats()
    
    l(f"Processing split: {sp} ({s})")
    
    l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}")
    
    d = await ld(src, sp, o, m)
    if not d:
        l(f"Failed to load dataset for split {sp}")
        return {}, 0
        
    q = cc['columns']['query']
    r = cc['columns']['response']
    t = cc['columns']['think']
    
    if q not in d.column_names or r not in d.column_names:
        l(f"Error: Required columns not found in dataset")
        return {}, 0
    
    categories = set(d["category"]) if "category" in d.column_names else set()
    if categories:
        l(f"Found categories in dataset: {', '.join(categories)}")
        
        cat_counts = {}
        for cat in categories:
            cat_counts[cat] = sum(1 for c in d["category"] if c == cat)
        for cat, count in cat_counts.items():
            l(f"Category '{cat}': {count} records")
    else:
        l(f"Warning: No 'category' column found in dataset, will use default category")
    
    total_records = len(d)
    l(f"Found {total_records} records with query and response columns for split {sp}")
    
    batch_size = a.batch_size if a.batch_size is not None else B
    checkpoint_interval = a.checkpoint_interval if a.checkpoint_interval is not None else C
    worker_count = a.workers if a.workers is not None else W
    
    l(f"Using {worker_count} workers, batches of {batch_size}, checkpoint every {checkpoint_interval}")
    
    semaphore = asyncio.Semaphore(worker_count)
    
    all_results = []
    success_results = []
    failed_results = []
    total_processed = 0
    
    total_needed = total_records
    telemetry_stats.last_log_time = time.time() - 30
    
    for start_idx in range(0, total_records, batch_size):
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, total_records)
        current_batch = d.select(range(start_idx, end_idx))
        current_batch_size = len(current_batch)
        
        l(f"Processing batch {start_idx//batch_size + 1}: records {start_idx+1} to {end_idx} (batch size: {current_batch_size})")
        
        task_list = []
        batch_results = []
        
        for i, row in enumerate(current_batch):
            idx = start_idx + i
            record_id = str(row.get('id', idx))
            
            task = asyncio.create_task(process_record_with_full_retries(row, idx, q, r, t, sp, semaphore))
            task.record_id = record_id
            task.row = row
            task.row_idx = idx
            task_list.append(task)
            
            if len(task_list) >= worker_count or i == len(current_batch) - 1:
                done, remaining_tasks = await asyncio.wait(
                    task_list, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                task_list = list(remaining_tasks)
                
                for completed_task in done:
                    try:
                        result = completed_task.result()
                        if "id" in result:
                            result["id"] = str(result["id"])
                        batch_results.append(result)
                        if result[t].startswith("ERROR:"):
                            failed_results.append(result)
                        else:
                            success_results.append(result)
                    except Exception as e:
                        record_id = getattr(completed_task, 'record_id', 'unknown')
                        row_idx = getattr(completed_task, 'row_idx', -1)
                        row = getattr(completed_task, 'row', None)
                        
                        l(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                        
                        error_record = {}
                        if row and "id" in row:
                            error_record["id"] = str(row["id"])
                        else:
                            error_record["id"] = f"error_{record_id}"
                            
                        if row:
                            error_record["prompt"] = f"Thinking process for query: {row[q][:50]}..."
                            error_record[t] = f"ERROR: Failed to generate thinking process: {str(e)}"
                            error_record[r] = row[r]
                            error_record[q] = row[q]
                            for c in row:
                                if c not in error_record and c not in [r, t, q, "id", "prompt"]:
                                    error_record[c] = row[c]
                        else:
                            error_record["prompt"] = "Unknown due to exception"
                            error_record[t] = f"ERROR: Failed to generate thinking process: {str(e)}"
                            error_record[r] = ""
                            error_record[q] = ""
                        
                        batch_results.append(error_record)
                        failed_results.append(error_record)
                    
                    if time.time() - telemetry_stats.last_log_time > 30:
                        l(telemetry_stats.get_telemetry_string(total_needed))
                        telemetry_stats.last_log_time = time.time()
        
        if task_list:
            done, _ = await asyncio.wait(task_list)
            for completed_task in done:
                try:
                    result = completed_task.result()
                    if "id" in result:
                        result["id"] = str(result["id"])
                    batch_results.append(result)
                    if result[t].startswith("ERROR:"):
                        failed_results.append(result)
                    else:
                        success_results.append(result)
                except Exception as e:
                    record_id = getattr(completed_task, 'record_id', 'unknown')
                    l(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                    
                    error_record = {
                        "id": f"error_{record_id}",
                        "prompt": "Unknown due to exception",
                        t: f"ERROR: Failed to generate thinking process: {str(e)}",
                        r: "",
                        q: ""
                    }
                    batch_results.append(error_record)
                    failed_results.append(error_record)
        
        all_results.extend(batch_results)
        total_processed += len(batch_results)
        batch_duration = time.time() - batch_start_time
        
        success_count = len(success_results)
        error_count = len(failed_results)
        
        l(f"Completed batch {start_idx//batch_size + 1} ({total_processed}/{total_records} records) in {batch_duration:.2f}s ({success_count} success, {error_count} errors)")
        
        l(telemetry_stats.get_telemetry_string(total_needed))
        telemetry_stats.last_log_time = time.time()
        
        if checkpoint_interval > 0 and total_processed % checkpoint_interval == 0:
            checkpoint_dataset = create_dataset_with_splits(success_results, failed_results, sp)
            await save_checkpoint(checkpoint_dataset, sp, total_processed, dr["ck"])
    
    ds = create_dataset_with_splits(success_results, failed_results, sp)
    success_count = telemetry_stats.successful_generations
    error_count = telemetry_stats.failed_generations
    l(f"Processing complete: {total_processed} total records ({success_count} success, {error_count} errors) in split {sp}")
    
    l(telemetry_stats.get_telemetry_string(total_needed))
    
    spd = os.path.join(dr["cs"], sp)
    os.makedirs(spd, exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved dataset with {len(success_results)} successful and {len(failed_results)} failed records to {spd}")
    
    return {sp: ds}, len(success_results)

def create_dataset_with_splits(success_records, failed_records, split_name):
    """Create a dataset with separate splits for successful and failed records."""
    empty_record = {
        "id": "0",  # Using string ID for consistency
        "prompt": "",
        "think": "",
        "response": "",
        "query": "",
        "category": ""
    }
    
    # Ensure all IDs are strings for consistency
    for record in success_records:
        if "id" in record:
            record["id"] = str(record["id"])
    
    for record in failed_records:
        if "id" in record:
            record["id"] = str(record["id"])
    
    splits = {}
    if success_records:
        splits[split_name] = Dataset.from_list(success_records)
    else:
        splits[split_name] = Dataset.from_list([empty_record]).select([])
        
    if failed_records:
        splits[f"{split_name}_failed"] = Dataset.from_list(failed_records)
    
    return DatasetDict(splits)

async def proc_sp(sp,s,src,o,m,dr,all_ds,total_recs):
    l(f"Processing split: {sp} ({s})")
    l(f"System prompt length: {len(cc['systems'][s])}");l(f"Metacog prompt length: {len(cc['metacogs'][s])}")
    l(f"Column mappings: query={cc['columns']['query']}, response={cc['columns']['response']}, think={cc['columns']['think']}") 
    d=await ld(src,sp,o,m)
    if not d:l(f"Failed to load dataset for split {sp}");return all_ds,total_recs
    q=cc['columns']['query'];r=cc['columns']['response'];t=cc['columns']['think'];
    if q not in d.column_names:l(f"Error: Query column '{q}' not found in dataset");return all_ds,total_recs
    if r not in d.column_names:l(f"Error: Response column '{r}' not found in dataset");return all_ds,total_recs
    l(f"Found {len(d)} records with query and response columns for split {sp}")
    
    all_results = []
    total_processed = 0
    batch_size = a.batch_size if a.batch_size is not None else B
    
    for start_idx in range(0, len(d), batch_size):
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, len(d))
        current_batch = d.select(range(start_idx, end_idx))
        l(f"Processing batch {start_idx//batch_size + 1}: records {start_idx+1} to {end_idx} (batch size: {len(current_batch)})")
        
        tasks = []
        for i, row in enumerate(current_batch):
            tasks.append(process_record(row, start_idx + i, q, r, t))
            
        batch_results = await asyncio.gather(*tasks)
        all_results.extend(batch_results)
        total_processed += len(batch_results)
        batch_duration = time.time() - batch_start_time
        l(f"Completed batch {start_idx//batch_size + 1} ({total_processed}/{len(d)} records) in {batch_duration:.2f}s")
    
    l(f"Prepared {len(all_results)} records with column order: id, prompt, think, response, query, [other fields]")
    ds=Dataset.from_list(all_results)
    spd=os.path.join(dr["cs"],sp)
    os.makedirs(spd,exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved {len(all_results)} records to local directory: {spd}")
    
    all_ds[sp]=ds
    total_recs+=len(all_results)
    return all_ds,total_recs
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
async def save_checkpoint(data, split, total_processed, checkpoint_dir):
    try:
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_{split}_{total_processed}")
        data.save_to_disk(checkpoint_path)
        l(f"Saved checkpoint at {checkpoint_path} after processing {total_processed} records")
        metadata = {
            "split": split,
            "processed": total_processed,
            "timestamp": time.time(),
            "checkpoint_path": checkpoint_path
        }
        with open(os.path.join(checkpoint_dir, f"meta_{split}.json"), 'w') as f:
            json.dump(metadata, f)
        return True
    except Exception as e:
        l(f"Error saving checkpoint: {str(e)}")
        return False
async def call_openai_api(ec,msg):
    try:
        async with AsyncOpenAI(base_url=ec['u'],api_key=ec.get('k',''))as c:
            r=await c.chat.completions.create(
                model=ec['m'],
                messages=msg,
                max_tokens=cc['max_tokens'],
                temperature=cc['temperature'],
                stream=False
            )
            if r and r.choices and r.choices[0].message:return r.choices[0].message.content
            else:raise Exception("No response content returned from API")
    except Exception as e:
        if "429" in str(e) or "TOO MANY" in str(e) or "rate limit" in str(e).lower():
            if fl and not test_mode: fl.info(f"Rate limit error: {str(e)}")
        else:
            l(f"OpenAI API error: {str(e)}")
        raise

async def call_ollama_api(ec,msg):
    try:
        c=AsyncClient(host=ec['u'])
        mt=cc['max_tokens']
        r=await c.chat(
            model=ec['m'],
            messages=msg,
            options={
                "temperature":cc['temperature'],
                "num_ctx":mt,
                "num_predict":mt
            },
            stream=False
        )
        if r and r.message:return r.message.content
        else:raise Exception("No response content returned from Ollama API")
    except Exception as e:
        l(f"Ollama API error: {str(e)}")
        raise

async def generate_thinking(r,s,i):
    global eps, telemetry_stats
    c=eps[i]
    c['in_use']=True
    try:
        record_id = r.get('id', '')
        
        t=time.time()
        p=c.get('p','').lower()
        n=c.get('n','')
        q=cc['columns']['query']
        r_c=cc['columns']['response']
        qu=r.get(q,"")
        rs=r.get(r_c,"")
        
        ct = r.get('category')
        
        lang_code = cc["splits"].get(s, "")
        
        min_length = cc.get('min_length', 0)
        
        l(f"[{record_id}] Starting request to {p}-{n} for category '{ct}'")
        
        if fl and not test_mode:
            fl.info(f"[{record_id}] Processing: {p}-{n}, split '{s}', category '{ct}', query {len(qu)} chars, response {len(rs)} chars")
        
        if not qu or not rs:
            c['in_use']=False
            c['last_call']=time.time()
            l(f"[{record_id}] ERROR: Empty input query or response")
            telemetry_stats.log_failure(record_id, s, "EmptyInput")
            raise ValueError("Empty input query or response")
        
        try:
            m, metacog_prompt = create_chat_messages(qu,rs,s,ct)
            if fl and not test_mode:
                fl.info(f"[{record_id}] Created chat messages with {len(m)} items")
        except Exception as e:
            l(f"[{record_id}] Error creating chat messages: {str(e)}")
            if fl and not test_mode:
                fl.info(f"[{record_id}] Error creating chat messages: {str(e)}")
            c['in_use']=False
            c['last_call']=time.time()
            telemetry_stats.log_failure(record_id, s, "PromptError")
            raise
        
        l(f"[{record_id}] Sending request to {p}-{n} ({cc['max_tokens']} max tokens, temperature {cc['temperature']})")
        
        try:
            async with asyncio.timeout(RT):
                if p=="openai":
                    result=await call_openai_api(c,m)
                elif p=="ollama":
                    result=await call_ollama_api(c,m)
                else:
                    c['in_use']=False
                    c['last_call']=time.time()
                    l(f"[{record_id}] ERROR: Unknown provider type: {p}")
                    telemetry_stats.log_failure(record_id, s, "UnknownProvider")
                    raise ValueError(f"Unknown provider type: {p}")
        except TimeoutError:
            l(f"[{record_id}] ERROR: Request timeout after {RT}s for {p}-{n}")
            if fl and not test_mode:
                fl.info(f"[{record_id}] Request timeout after {RT}s for {p}-{n}")
            c['in_use']=False
            c['last_call']=time.time() if p == "ollama" else time.time() + EC/2
            telemetry_stats.log_failure(record_id, s, "Timeout")
            raise
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "TOO MANY" in err_msg or "rate limit" in err_msg.lower():
                l(f"[{record_id}] Rate limit hit on {p}-{n}")
                if fl and not test_mode:
                    fl.info(f"[{record_id}] ERROR: API call failed: {err_msg}")
            else:
                l(f"[{record_id}] ERROR: API call failed: {err_msg}")
                if fl and not test_mode:
                    fl.info(f"[{record_id}] ERROR: API call failed: {err_msg}")
            
            c['in_use']=False
            c['last_call']=time.time()
            error_type = "RateLimit" if "429" in err_msg or "rate limit" in err_msg.lower() else type(e).__name__
            telemetry_stats.log_failure(record_id, s, error_type)
            raise
            
        e=round(time.time()-t,2)
        
        try:
            check_min_length(result, min_length)
            l(f"[{record_id}] Response received ({len(result)} chars) in {e:.2f}s")
        except ValueError as e:
            l(f"[{record_id}] ERROR: Response too short: {str(e)}")
            if fl and not test_mode:
                fl.info(f"[{record_id}] Response too short: {str(e)}")
                
            c['in_use']=False
            c['last_call']=time.time()
            
            telemetry_stats.log_failure(record_id, s, "ResponseTooShort")
            raise
        
        if not test_mode and dr and "t" in dr:
            temp_dir = os.path.join(dr["t"], lang_code)
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, f"{record_id}.txt")
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                if fl: fl.info(f"[{record_id}] Saved response to {temp_file}")
            except Exception:
                pass
            
        c['in_use']=False
        c['last_call']=time.time()
        l(f"[{record_id}] Successfully generated reasoning ({len(result)} chars) in {e:.2f}s using {p}-{n}")
        if fl and not test_mode:
            fl.info(f"[{record_id}] Generated reasoning ({len(result)} chars) in {e:.2f}s using {p}-{n}")
        
        telemetry_stats.log_success(record_id, s)
        
        if time.time() - telemetry_stats.last_log_time > 30:
            total_records_estimate = cc.get('max_records', 100) or 100
            l(telemetry_stats.get_telemetry_string(total_records_estimate))
            telemetry_stats.last_log_time = time.time()
            
        return result, e, metacog_prompt
    except Exception as e:
        if'c'in locals():
            c['in_use']=False
            c['last_call']=time.time()
            
        if 'record_id' in locals() and 's' in locals():
            error_type = type(e).__name__
            telemetry_stats.log_failure(record_id, s, error_type)
        raise

def create_chat_messages(q,r,sp,c):
    if c not in ["dark_thoughts", "benign"]:
        raise ValueError(f"Invalid category '{c}' - must be 'dark_thoughts' or 'benign'")
    
    lang_code = cc["splits"].get(sp, "")
    sys_prompts = cc.get("systems", {})
    metacog_prompts = cc.get("metacogs", {})
    
    system_prompt = sys_prompts[c][lang_code]
    metacog_prompt = metacog_prompts[c][lang_code]
    
    if fl and not test_mode:
        fl.info(f"Chat created for category '{c}': system {len(system_prompt)}, query {len(q)}, response {len(r)}, metacog {len(metacog_prompt)} chars")
        
    return[
        {"role":"system","content":system_prompt},
        {"role":"user","content":q},
        {"role":"assistant","content":r},
        {"role":"user","content":metacog_prompt}
    ], metacog_prompt

def should_retry_exception(exception):
    if isinstance(exception, ValueError) and "shorter than minimum required length" in str(exception):
        return True
    
    error_message = str(exception).lower()
    if "429" in error_message or "too many tokens" in error_message or "rate limit" in error_message:
        return True
        
    if "timeout" in error_message:
        return True
        
    return False

@retry(
    stop=stop_after_attempt(R), 
    wait=wait_random(min=1, max=3),
    retry=should_retry_exception,
    reraise=True
)
async def process_record(row, idx, query_col, response_col, think_col, split, semaphore):
    # Convert record_id to string for consistency
    record_id = str(row.get("id", idx))
    
    async with semaphore:
        try:
            if fl and not test_mode:
                fl.info(f"[{record_id}] Starting to process record")
            
            endpoint_idx = gne(eps)
            
            # Fixed: Access statistics properly as a dictionary property
            retry_state = getattr(process_record, 'retry', None)
            current_attempt = 1
            if retry_state and hasattr(retry_state, 'statistics'):
                stats = retry_state.statistics
                if isinstance(stats, dict):
                    current_attempt = stats.get('attempt_number', 1)
                
            if current_attempt > 1:  # If this is a retry
                l(f"[{record_id}] Attempt {current_attempt}/{R}: Getting endpoint for retry")
                
            reasoning, elapsed_time, metacog_prompt = await generate_thinking(row, split, endpoint_idx)
            
            rd = {}
            if "id" in row:
                rd["id"] = str(row["id"])  # Convert to string
            else:
                rd["id"] = str(idx)  # Use string version of index
                
            rd["prompt"] = metacog_prompt
            rd[think_col] = reasoning
            rd[response_col] = row[response_col]
            rd[query_col] = row[query_col]
            for c in row:
                if c not in rd and c not in [response_col, think_col, query_col, "id", "prompt"]:
                    rd[c] = row[c]
            
            l(f"[{record_id}] Successfully completed processing in {elapsed_time:.2f}s")
            
            if fl and not test_mode:
                fl.info(f"[{record_id}] Successfully processed in {elapsed_time:.2f}s")
            return rd
                
        except Exception as e:
            # Get the current retry attempt number - fixed to properly access statistics
            retry_state = getattr(process_record, 'retry', None)
            current_attempt = 1
            if retry_state and hasattr(retry_state, 'statistics'):
                stats = retry_state.statistics
                if isinstance(stats, dict):
                    current_attempt = stats.get('attempt_number', 1)
                
            max_attempts = R
            
            if current_attempt < max_attempts:
                l(f"[{record_id}] RETRY {current_attempt}/{max_attempts}: {type(e).__name__} - {str(e)[:100]}")
                # Don't handle the exception here - let it propagate to trigger the retry
                raise e
            else:
                l(f"[{record_id}] ERROR after all {max_attempts} retries: {type(e).__name__} - {str(e)[:100]}")
                raise e

async def process_record_with_full_retries(row, idx, query_col, response_col, think_col, split, semaphore):
    """
    Wrapper around process_record that ensures all retry attempts are completed
    before giving up on a record.
    """
    record_id = str(row.get("id", idx))
    retry_count = 0
    max_retries = R
    
    while retry_count < max_retries:
        try:
            # Try to process the record
            return await process_record(row, idx, query_col, response_col, think_col, split, semaphore)
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                l(f"[{record_id}] ERROR after exhausting all {max_retries} retries: {type(e).__name__} - {str(e)[:100]}")
                # Re-raise the exception after all retries are exhausted
                raise
            else:
                backoff_time = random.uniform(1, 3)
                l(f"[{record_id}] Manual RETRY {retry_count}/{max_retries}: {type(e).__name__} - {str(e)[:100]} (waiting {backoff_time:.2f}s)")
                await asyncio.sleep(backoff_time)  # Add a backoff delay
                # Let the loop continue to retry

async def main(args):
    try:
        global dr, cc, eps, test_mode, a, telemetry_stats
        a = args
        test_mode = a.test
        telemetry_stats = TelemetryStats()
        
        dr = await setup_dirs(a) if not test_mode else {}
        if not test_mode:l(f"Run ID: {dr['r']}");l(f"Data dir: {dr['d']}");l(f"Config URL: {a.config}")
        cc = await g(a.config)
        if not cc:l("Failed to load config");return
        k,m = await v(cc)
        if not k:l(f"Invalid configuration: {m}");return
        l("Config successfully loaded")
        
        if not test_mode and "splits" in cc and "t" in dr:
            for split, lang_code in cc.get("splits", {}).items():
                lang_dir = os.path.join(dr["t"], lang_code)
                os.makedirs(lang_dir, exist_ok=True)
                l(f"Created temp directory for language: {lang_code}")
                
        l(f"Config loaded with {len(cc.get('endpoints',[]))} endpoints")
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
        batch_size = a.batch_size if a.batch_size is not None else B
        checkpoint_interval = a.checkpoint_interval if a.checkpoint_interval is not None else C
        l(f"Using batch size of {batch_size} for processing records")
        l(f"Using checkpoint interval of {checkpoint_interval} records")
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
        l(f"Finished processing all splits")
    except Exception as e:
        tb = traceback.format_exc()
        l(f"Fatal error: {str(e)}\n{tb}")
        raise e
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
    p.add_argument("--batch-size",type=int,default=B,help="Number of records to process in a batch (default: 100)")
    p.add_argument("--checkpoint-interval",type=int,default=C,help="Interval to save intermediate checkpoints (default: 500)")
    args=p.parse_args()
    global test_mode,cl,fl
    test_mode=args.test
    try:cl,fl=s(args.log_dir,test_mode);asyncio.run(main(args))
    except Exception as e:print(f"Fatal error: {e}");exit(1)