import argparse as ap,os,asyncio,logging,time,requests,random,json
from tenacity import retry,wait_random,stop_after_attempt
from datasets import load_dataset,Dataset,DatasetDict
from asyncio import TimeoutError
from openai import AsyncOpenAI
from ollama import AsyncClient

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

# Remove the redundant should_retry_exception function since we'll retry on all errors

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
    
    # Check if split name exists in systems categories
    system_categories = ["dark_thoughts", "benign"]
    found_in_systems = False
    for category in system_categories:
        if category in c["systems"] and p in c["systems"][category]:
            found_in_systems = True
            break
    if not found_in_systems:return False,f"No '{p}' in systems categories"
    
    # Check if split name exists in metacogs categories
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
    # First, find all available endpoints that have cooled down (skip cooldown for Ollama)
    for i,ep in enumerate(e):
        provider = ep.get('p', '').lower()
        # Ollama endpoints don't need cooldown, others need EC seconds
        if not ep['in_use'] and (provider == "ollama" or n-ep['last_call']>=EC):
            a.append((i,ep))
    
    # If no endpoints are available, find the one that will be available soonest
    if not a:
        # For finding soonest ready, respect the per-provider cooldown
        s=min(e, key=lambda x: x['last_call'] if x.get('p','').lower() == "ollama" else (
            x['last_call']+EC if not x['in_use'] else float('inf')))
        i=e.index(s)
        
        # Only wait if it's not an Ollama endpoint
        if s.get('p','').lower() != "ollama":
            w=max(0,(s['last_call']+EC)-n)
            if w>0:
                l(f"All endpoints busy or cooling down, will wait {w:.2f}s for next available")
                time.sleep(w)
        return i
    
    # Sort available endpoints by last call time (oldest first)
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
    
    # No need to choose a single category here - we'll use the one specified in each record
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
    
    # Log available categories in the dataset without additional verification
    categories = set(d["category"]) if "category" in d.column_names else set()
    if categories:
        l(f"Found categories in dataset: {', '.join(categories)}")
        
        # Count records by category
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
    
    # Create a semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(worker_count)
    
    all_results = []
    success_results = []
    failed_results = []
    total_processed = 0
    
    # Initialize telemetry
    total_needed = total_records
    telemetry_stats.last_log_time = time.time() - 30  # Force initial telemetry message
    
    for start_idx in range(0, total_records, batch_size):
        batch_start_time = time.time()
        end_idx = min(start_idx + batch_size, total_records)
        current_batch = d.select(range(start_idx, end_idx))
        current_batch_size = len(current_batch)
        
        l(f"Processing batch {start_idx//batch_size + 1}: records {start_idx+1} to {end_idx} (batch size: {current_batch_size})")
        
        # Create a list to hold tasks that are currently running
        pending_tasks = []
        batch_results = []
        
        # Process records sequentially with limited concurrency
        for i, row in enumerate(current_batch):
            record_id = row.get('id', start_idx + i)
            
            # Create a new task and add it to pending_tasks
            task = asyncio.create_task(process_record(row, start_idx + i, q, r, t, sp, semaphore))
            pending_tasks.append(task)
            
            # If we've reached the worker limit or this is the last item, wait for some tasks to complete
            if len(pending_tasks) >= worker_count or i == len(current_batch) - 1:
                # Wait for at least one task to complete
                done, pending_tasks = await asyncio.wait(
                    pending_tasks, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for completed_task in done:
                    try:
                        result = completed_task.result()
                        batch_results.append(result)
                        if result[t].startswith("ERROR:"):
                            failed_results.append(result)
                        else:
                            success_results.append(result)
                    except Exception as e:
                        l(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                        
                        # Create error record
                        error_record = {}
                        if "id" in row:
                            error_record["id"] = row["id"]
                        error_record["prompt"] = f"Thinking process for query: {row[q][:50]}..."
                        error_record[t] = f"ERROR: Failed to generate thinking process: {str(e)}"
                        error_record[r] = row[r]
                        error_record[q] = row[q]
                        for c in row:
                            if c not in error_record and c not in [r, t, q, "id", "prompt"]:
                                error_record[c] = row[c]
                        
                        batch_results.append(error_record)
                        failed_results.append(error_record)
                    
                    # Periodic telemetry check
                    if time.time() - telemetry_stats.last_log_time > 30:
                        l(telemetry_stats.get_telemetry_string(total_needed))
                        telemetry_stats.last_log_time = time.time()
        
        # Wait for any remaining tasks to complete
        if pending_tasks:
            done, _ = await asyncio.wait(pending_tasks)
            for completed_task in done:
                try:
                    result = completed_task.result()
                    batch_results.append(result)
                    if result[t].startswith("ERROR:"):
                        failed_results.append(result)
                    else:
                        success_results.append(result)
                except Exception as e:
                    record_id = "unknown"  # We can't know which record this was
                    l(f"[{record_id}] ERROR: Failed to process record after all retries: {str(e)}")
                    
                    # We can't create a proper error record here since we don't know which row it was
                    error_record = {
                        "id": f"unknown_{len(failed_results)}",
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
        
        success_count = telemetry_stats.successful_generations
        error_count = telemetry_stats.failed_generations
        
        l(f"Completed batch {start_idx//batch_size + 1} ({total_processed}/{total_records} records) in {batch_duration:.2f}s ({success_count} success, {error_count} errors)")
        
        # Always log batch telemetry regardless of timing
        l(telemetry_stats.get_telemetry_string(total_needed))
        telemetry_stats.last_log_time = time.time()
        
        if checkpoint_interval > 0 and total_processed % checkpoint_interval == 0:
            checkpoint_dataset = create_dataset_with_splits(success_results, failed_results, sp)
            await save_checkpoint(checkpoint_dataset, sp, total_processed, dr["ck"])
    
    # Create final dataset with success and failed splits
    ds = create_dataset_with_splits(success_results, failed_results, sp)
    success_count = telemetry_stats.successful_generations
    error_count = telemetry_stats.failed_generations
    l(f"Processing complete: {total_processed} total records ({success_count} success, {error_count} errors) in split {sp}")
    
    # Final telemetry
    l(telemetry_stats.get_telemetry_string(total_needed))
    
    # Save to disk
    spd = os.path.join(dr["cs"], sp)
    os.makedirs(spd, exist_ok=True)
    ds.save_to_disk(spd)
    l(f"Saved dataset with {len(success_results)} successful and {len(failed_results)} failed records to {spd}")
    
    return {sp: ds}, len(success_results)

def create_dataset_with_splits(success_records, failed_records, split_name):
    """Create a dataset with separate splits for successful and failed records."""
    empty_record = {
        "id": 0,
        "prompt": "",
        "think": "",
        "response": "",
        "query": "",
        "category": ""
    }
    
    # Create datasets for each type
    splits = {}
    if success_records:
        splits[split_name] = Dataset.from_list(success_records)
    else:
        # Create an empty dataset with the right schema
        splits[split_name] = Dataset.from_list([empty_record]).select([])
        
    # Add failed records if any exist
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
    # Create base directories only
    for dr in[d,rd,cs,t,ck]:os.makedirs(dr,exist_ok=True)
    # We'll create language-specific directories later after loading config
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
            # Log rate limit errors only to file, not to console to reduce clutter
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
        
        # Get the category from the record - no default or fallback
        ct = r.get('category')
        
        # Get language code from the split
        lang_code = cc["splits"].get(s, "")
        
        min_length = cc.get('min_length', 0)
        
        # Log when record processing starts, but with clear indication this is creating a request
        l(f"[{record_id}] Starting request to {p}-{n} for category '{ct}'")
        
        # Only detailed logging goes to file
        if fl and not test_mode:
            fl.info(f"[{record_id}] Processing: {p}-{n}, split '{s}', category '{ct}', query {len(qu)} chars, response {len(rs)} chars")
        
        if not qu or not rs:
            c['in_use']=False
            c['last_call']=time.time()
            l(f"[{record_id}] ERROR: Empty input query or response")
            telemetry_stats.log_failure(record_id, s, "EmptyInput")
            return "",0.0
        
        try:
            # Use the regular function directly without awaiting
            # Now returns both messages and metacog_prompt
            m, metacog_prompt = create_chat_messages(qu,rs,s,ct)
            # Only log this to file, not to console to reduce clutter
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
                    raise Exception(f"Unknown provider type: {p}")
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
            # Filter rate limit messages for console but keep full logs in file
            if "429" in err_msg or "TOO MANY" in err_msg or "rate limit" in err_msg.lower():
                # Log concise rate limit message to console
                l(f"[{record_id}] Rate limit hit on {p}-{n}")
                # Log full details only to file
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
        
        # Check minimum length before saving - simplify this logic
        try:
            check_min_length(result, min_length)
            # Log success with character count
            l(f"[{record_id}] Response received ({len(result)} chars) in {e:.2f}s")
        except ValueError as e:
            l(f"[{record_id}] ERROR: Response too short: {str(e)}")
            if fl and not test_mode:
                fl.info(f"[{record_id}] Response too short: {str(e)}")
                
            # Mark the endpoint as not in use
            c['in_use']=False
            # Apply cooldown like any other error
            c['last_call']=time.time()
            
            telemetry_stats.log_failure(record_id, s, "ResponseTooShort")
            # Re-raise to trigger the retry mechanism
            raise
        
        # Save the response to temp file - using language code instead of split name
        if not test_mode and dr and "t" in dr:
            # Use language code (e.g., "en", "zh") for the directory 
            temp_dir = os.path.join(dr["t"], lang_code)
            os.makedirs(temp_dir, exist_ok=True)
            # Just use record_id for the filename without timestamp
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
        
        # Simply check if enough time has passed and log telemetry if needed
        # Don't reference total_needed which isn't available in this scope
        if time.time() - telemetry_stats.last_log_time > 30:
            # Use an estimated value for total based on what we know
            total_records_estimate = cc.get('max_records', 100) or 100
            l(telemetry_stats.get_telemetry_string(total_records_estimate))
            telemetry_stats.last_log_time = time.time()
            
        # Return metacog_prompt along with the result and elapsed time
        return result, e, metacog_prompt
    except Exception as e:
        if'c'in locals():
            c['in_use']=False
            # Always apply cooldown for all errors - simplify logic
            c['last_call']=time.time()
        raise

# Change from async to regular function since it doesn't need to be async
def create_chat_messages(q,r,sp,c):
    # Verify category is valid with no fallback - will raise error if not valid
    if c not in ["dark_thoughts", "benign"]:
        raise ValueError(f"Invalid category '{c}' - must be 'dark_thoughts' or 'benign'")
    
    lang_code = cc["splits"].get(sp, "")
    sys_prompts = cc.get("systems", {})
    metacog_prompts = cc.get("metacogs", {})
    
    system_prompt = sys_prompts[c][lang_code]
    metacog_prompt = metacog_prompts[c][lang_code]
    
    # Only detailed logging goes to file, add category information to log
    if fl and not test_mode:
        fl.info(f"Chat created for category '{c}': system {len(system_prompt)}, query {len(q)}, response {len(r)}, metacog {len(metacog_prompt)} chars")
        
    return[
        {"role":"system","content":system_prompt},
        {"role":"user","content":q},
        {"role":"assistant","content":r},
        {"role":"user","content":metacog_prompt}
    ], metacog_prompt

@retry(
    stop=stop_after_attempt(R), 
    wait=wait_random(min=1, max=3),  # Use consistent wait timing
    reraise=True
)
async def process_record(row, idx, query_col, response_col, think_col, split, semaphore):
    record_id = row.get("id", idx)
    
    # Use the semaphore to limit concurrent API calls
    async with semaphore:
        try:
            # Log at the start of processing but don't output to console to avoid cluttering
            if fl and not test_mode:
                fl.info(f"[{record_id}] Starting to process record")
            
            # Get endpoint and generate thinking - Tenacity will handle retries
            endpoint_idx = gne(eps)
            
            # Add debugging to track retries
            current_attempt = getattr(process_record.retry, 'statistics', {}).get('attempt_number', 0)
            if current_attempt > 0:  # If this is a retry
                l(f"[{record_id}] Attempt {current_attempt+1}/{R}: Getting endpoint for retry")
                
            reasoning, elapsed_time, metacog_prompt = await generate_thinking(row, split, endpoint_idx)
            
            # Build result dictionary
            rd = {}
            if "id" in row:
                rd["id"] = row["id"]
            rd["prompt"] = metacog_prompt  # Store the actual metacog prompt for debugging
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
            # Handle the retry logic properly
            current_attempt = getattr(process_record.retry, 'statistics', {}).get('attempt_number', 0) + 1
            max_attempts = R
            
            if current_attempt < max_attempts:
                l(f"[{record_id}] RETRY {current_attempt}/{max_attempts}: {type(e).__name__} - {str(e)[:100]}")
            else:
                l(f"[{record_id}] ERROR after {max_attempts} retries: {type(e).__name__} - {str(e)[:100]}")
            
            # Re-raise to trigger the retry mechanism
            raise
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
        
        # Now that we have the config, create language directories
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
            l(f"Preparing to push unified dataset to {dst}")
            hft=cc.get('hf_token');prv=cc.get('private',True)
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
    p.add_argument("--batch-size",type=int,default=B,help="Number of records to process in a batch (default: 100)")
    p.add_argument("--checkpoint-interval",type=int,default=C,help="Interval to save intermediate checkpoints (default: 500)")
    args=p.parse_args()
    global test_mode,cl,fl
    test_mode=args.test
    try:cl,fl=s(args.log_dir,test_mode);asyncio.run(main(args))
    except Exception as e:print(f"Fatal error: {e}");exit(1)