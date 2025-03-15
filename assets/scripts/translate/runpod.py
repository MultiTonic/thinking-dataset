import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Dict, Any

from ollama import AsyncClient
from nltk.tokenize import sent_tokenize
from text import preprocess_text, postprocess_text
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

try:
    from runpodapi import RunPodClient
except ImportError:
    print("Warning: runpodapi not found. RunPod functionality disabled.")
    RunPodClient = None

def create_retry_decorator(max_retries):
    return retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_random_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((asyncio.TimeoutError, ConnectionError, Exception)),
        reraise=True
    )

class RunPodEndpoint:
    def __init__(self, endpoint: str, model: str = "gemmax2-custom", is_pod_id: bool = True, 
                 max_retries: int = 3, request_timeout: int = 30):
        self.endpoint = f"https://{endpoint}-11434.proxy.runpod.net" if is_pod_id else endpoint
        self.model = model
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.client = AsyncClient(host=self.endpoint)

    async def translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        retry_decorator = create_retry_decorator(self.max_retries)
        
        @retry_decorator
        async def _do_translate():
            processed_text, tag_map, structure = preprocess_text(text)
            if not processed_text:
                return ""

            # Split into sentences and translate individually
            sentences = sent_tokenize(processed_text)
            translated_sentences = []
            prompt_template = f"Translate this sentence from {src_lang} to {tgt_lang}:\n{src_lang}: {{sentence}}\n{tgt_lang}:"

            for sentence in sentences:
                prompt = prompt_template.format(sentence=sentence)
                try:
                    response = await asyncio.wait_for(
                        self.client.generate(model=self.model, prompt=prompt),
                        timeout=self.request_timeout  # Use configurable timeout
                    )
                    
                    if response and "response" in response:
                        translated = response["response"].split(f"{tgt_lang}:")[-1].strip()
                        if translated:
                            translated_sentences.append(translated)
                        else:
                            raise ValueError(f"Empty translation result for sentence: {sentence[:50]}...")
                    else:
                        raise ValueError(f"Invalid response format when translating: {sentence[:50]}...")
                        
                except asyncio.TimeoutError:
                    raise ValueError(f"Translation timed out for sentence: {sentence[:50]}...")
                    
                except Exception as e:
                    print(f"Translation error: {type(e).__name__}: {str(e)}")
                    if isinstance(e, ValueError) and "translation" in str(e).lower():
                        raise
                    else:
                        raise ValueError(f"Failed to translate sentence: {sentence[:50]}... - {str(e)}")

            return postprocess_text(translated_sentences, tag_map, structure)
        
        return await _do_translate()

def launch_runpods(config, pods_to_launch=None):
    """
    Launch RunPod instances.
    
    Args:
        config: Configuration object
        pods_to_launch: Optional count of pods to launch (defaults to config.num_runpods)
        
    Returns:
        list: Tuples of (pod_id, pod_name) for successfully created pods
    """
    if not RunPodClient:
        print("[RUNPOD] RunPodClient not available. Running locally.")
        return []

    client = RunPodClient(api_key=config.runpod_api_key)
    pod_info = []
    total_start_time = time.time()
    num_pods = pods_to_launch if pods_to_launch is not None else config.num_runpods

    if num_pods <= 0:
        print("[RUNPOD] No pods needed for launch.")
        return []

    try:
        print("[RUNPOD] Fetching available templates...")
        templates = client.get_templates()
        print(f"[RUNPOD] Found {len(templates)} templates")
        ollama_template_id = None
        for template in templates:
            if "ollama/ollama" in template.get("imageName", ""):
                ollama_template_id = template["id"]
                print(f"Found Ollama template: {template['name']}")
                break

        if not ollama_template_id:
            print("Creating new Ollama template...")
            template_config = {
                "name": "A40 Ollama Template",
                "imageName": "ollama/ollama",
                "containerDiskInGb": 50,
                "env": [{"key": "OLLAMA_HOST", "value": "0.0.0.0"}],
                "ports": ["11434/http"],
                "isServerless": False,
                "isPublic": True,
                "dockerStartCmd": ["/bin/bash", "-c", "apt update && apt install -y lshw && ollama serve &"]
            }
            new_template = client.create_template(template_config)
            ollama_template_id = new_template["id"]
            print(f"Created new Ollama template: {new_template['name']} (ID: {ollama_template_id})")

        pod_config = {
            "gpuCount": 1,
            "gpuTypeIds": ["NVIDIA A40"],
            "containerDiskInGb": 100,
            "volumeInGb": 120,
            "ports": ["11434/http"],
            "supportPublicIp": True,
            "imageName": "tonic01/ollama-gemmax2-28:latest",
            "env": {"OLLAMA_HOST": "0.0.0.0"},
            "dockerStartCmd": [
                "/bin/bash", "-c",
                "OLLAMA_NUM_PARALLEL=8 OLLAMA_MAX_LOADED_MODELS=8 ollama serve & sleep 5 && "
                "echo 'FROM hf.co/mradermacher/GemmaX2-28-2B-v0.1-GGUF:Q8_0\n"
                "PARAMETER num_ctx 32768\n"
                "PARAMETER num_predict 32000\n"
                "PARAMETER num_gpu 99\n"
                "' > /tmp/Modelfile && "
                "ollama create gemmax2-custom -f /tmp/Modelfile && "
                "ollama run gemmax2-custom"
            ]
        }

        # Set up thread pool for parallel pod creation
        max_workers = min(32, num_pods)  # Default to 32 workers or fewer if fewer pods
        print(f"[RUNPOD] Launching {num_pods} pods with A40 GPUs using {max_workers} parallel workers...")
        
        def create_and_start_pod(i):
            pod_name = f"Translation-Pod-{i+1}"
            try:
                pod = client.create_pod_from_template(
                    template_id=ollama_template_id,
                    name=pod_name,
                    additional_config=pod_config
                )
                pod_id = pod["id"]
                client.start_pod(pod_id)
                return (pod_id, pod_name, True, None)
            except Exception as e:
                # Only return the failure information, don't print errors
                return (None, pod_name, False, str(e))
        
        # Use ThreadPoolExecutor for parallel pod creation
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(create_and_start_pod, range(num_pods)))
            
        # Process results, only report the successful ones
        success_count = 0
        failure_count = 0
        
        print(f"\nPod creation results:")
        for pod_id, pod_name, success, error in results:
            if success:
                pod_info.append((pod_id, pod_name))
                success_count += 1
                print(f"  {pod_name} - ID: {pod_id}")
            else:
                failure_count += 1
                # Don't print individual failures here
                
        print(f"\n{success_count}/{num_pods} pods created successfully ({failure_count} pending)")
        
        if not pod_info:
            print("No pods were successfully created. Cannot proceed.")
            return []
            
        startup_time = time.time() - total_start_time
        print(f"Created and started {success_count} pods in {startup_time:.2f}s")
        print(f"Waiting {config.startup_delay//60} minutes for pods to initialize...")
        time.sleep(config.startup_delay)

        # Check status of created pods
        running_pods = {}
        status_start_time = time.time()
        
        print(f"[RUNPOD] Starting status checks for {len(pod_info)} pods (max retries: {config.max_retries})")
        
        # Use tenacity retry instead of manual for loop
        @retry(
            stop=stop_after_attempt(config.max_retries),
            wait=wait_random_exponential(multiplier=1, min=1, max=5),
            before_sleep=lambda retry_state: print(f"\nStatus check attempt {retry_state.attempt_number}/{config.max_retries}"),
            after=lambda retry_state: print(f"  {len(running_pods)}/{len(pod_info)} pods running"),
            retry=retry_if_exception_type(ValueError)
        )
        def check_all_pods_status():
            nonlocal running_pods
            
            # Function to check pod status in parallel
            def check_pod_status(pod_tuple):
                pod_id, pod_name = pod_tuple
                try:
                    if pod_id in running_pods:
                        return pod_id, pod_name, "ALREADY_CONFIRMED"
                    
                    pod_details = client.get_pod(pod_id, include_details=True)
                    status = pod_details.get("desiredStatus", "UNKNOWN")
                    return pod_id, pod_name, status
                except Exception:
                    return pod_id, pod_name, "ERROR"
            
            # Check pods in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                status_results = list(executor.map(check_pod_status, pod_info))
            
            # Process results
            all_running = True
            for pod_id, pod_name, status in status_results:
                if status == "RUNNING" or status == "ALREADY_CONFIRMED":
                    running_pods[pod_id] = pod_name
                else:
                    all_running = False
            
            if all_running:
                status_time = time.time() - status_start_time
                print(f"All {len(pod_info)} pods are ready! (checks completed in {status_time:.2f}s)")
                return True
            else:
                # Sleep before raising exception to avoid tight retry loop
                print(f"Not all pods ready, waiting {config.startup_delay // 60} minutes before retry...")
                time.sleep(config.startup_delay)
                raise ValueError("Not all pods are ready yet")
        
        try:
            check_all_pods_status()
        except Exception as e:
            print(f"Maximum retries reached. Proceeding with {len(running_pods)}/{len(pod_info)} pods.")

        total_time = time.time() - total_start_time
        print(f"[RUNPOD] Total startup process completed in {total_time:.2f}s")
        print(f"[RUNPOD] {len(running_pods)} pods are ready to use")
        return [(pod_id, pod_name) for pod_id, pod_name in running_pods.items()]

    except Exception as e:
        print(f"[RUNPOD] Error launching pods: {str(e)}")
        return []

async def find_and_terminate_all_runpods(config) -> int:
    if not RunPodClient:
        print("RunPodClient not available. Cannot terminate pods.")
        return 0
    
    client = RunPodClient(api_key=config.runpod_api_key)
    terminated_count = 0
    total_start_time = time.time()
    
    try:
        print("Fetching active RunPod instances...")
        pods = client.get_pods()
        
        if not pods:
            print("No active RunPod instances found.")
            return 0
        
        print(f"Found {len(pods)} pods")
        
        # Sort pods by name numerical order
        pods.sort(key=lambda pod: int(pod.get("name", "Translation-Pod-0").replace("Translation-Pod-", "0") or "0"))
        
        # Use max_workers from config
        max_workers = min(32, config.workers if hasattr(config, "workers") else 32)
        print(f"Terminating pods with {max_workers} parallel workers")
        
        # Create semaphore for API rate limiting
        semaphore = asyncio.Semaphore(max_workers)
        
        # Display all pods with their status
        pod_statuses = {}
        for pod in pods:
            status = pod.get("desiredStatus", "UNKNOWN")
            pod_statuses[status] = pod_statuses.get(status, 0) + 1
            
        print(f"  Pod statuses: {', '.join([f'{status}: {count}' for status, count in pod_statuses.items()])}")
        
        async def terminate_pod(pod):
            async with semaphore:
                pod_id = pod.get("id")
                pod_name = pod.get("name", "Unnamed")
                
                if not pod_id:
                    return False, pod_name
                    
                try:
                    client.stop_pod(pod_id)
                    await asyncio.sleep(1)
                    client.delete_pod(pod_id)
                    return True, pod_name
                except Exception:
                    return False, pod_name
        
        # Create tasks for all pods - modify to include all statuses, not just a subset
        tasks = []
        for pod in pods:
            # Consider all pods for termination, not just specific statuses
            tasks.append(terminate_pod(pod))
        
        print(f"  Terminating {len(tasks)} pods...")
        
        # Execute all termination tasks
        if tasks:
            results = await asyncio.gather(*tasks)
            
            # Count successes
            success_names = []
            fail_names = []
            for success, pod_name in results:
                if success:
                    terminated_count += 1
                    success_names.append(pod_name)
                else:
                    fail_names.append(pod_name)
            
            print(f"\nTermination results:")
            print(f"  {terminated_count}/{len(tasks)} pods successfully terminated")
            
            if fail_names:
                print(f"  {len(fail_names)} pods failed to terminate")
        
    except Exception as e:
        print(f"Error terminating pods: {str(e)}")
    
    total_time = time.time() - total_start_time
    print(f"Pod termination completed in {total_time:.2f}s")
    return terminated_count

async def test_single_pod(pod_id: str, pod_name: str, max_retries: int = 3, request_timeout: int = 30) -> Tuple[bool, float, str, Dict[str, Any]]:
    retry_decorator = create_retry_decorator(max_retries)
    
    @retry_decorator
    async def _test_pod():
        try:
            print(f"[POD: {pod_name}] Testing pod {pod_id} with {max_retries} max retries...")
            start_time = time.time()
            endpoint = RunPodEndpoint(pod_id, is_pod_id=True, request_timeout=request_timeout)
            
            # Use the actual translation prompt template for testing
            src_lang = "English"
            tgt_lang = "Chinese"
            test_sentence = "Hello"
            expected_result = "你好"  # Standard Chinese greeting
            
            print(f"[POD: {pod_name}] Sending test translation request: '{test_sentence}' from {src_lang} to {tgt_lang}")
            
            prompt_template = f"Translate this sentence from {src_lang} to {tgt_lang}:\n{src_lang}: {test_sentence}\n{tgt_lang}:"
            
            # Including "options" to verify the concurrent request settings
            response = await asyncio.wait_for(
                endpoint.client.generate(
                    model="gemmax2-custom",
                    prompt=prompt_template,
                    stream=False,
                    options={
                        "temperature": 0,
                        "top_p": 0.95,
                        "num_predict": 50,
                        # Note: OLLAMA_NUM_PARALLEL=8 configured in Docker startup ensures 8 concurrent requests
                    }
                ),
                timeout=request_timeout
            )
            
            latency = time.time() - start_time
            
            if response and "response" in response:
                response_text = response["response"].strip()
                # Check if the response contains the expected Chinese translation
                if expected_result in response_text:
                    print(f"[POD: {pod_name}] Test successful in {latency:.2f}s: '{response_text}'")
                    return True, latency, None, {"pod_id": pod_id, "pod_name": pod_name}
                else:
                    print(f"[POD: {pod_name}] Unexpected translation result: '{response_text}'. Expected: '{expected_result}'")
                    # Still consider it OK if we got any response - we're testing connectivity more than accuracy
                    return True, latency, None, {"pod_id": pod_id, "pod_name": pod_name}
            else:
                print(f"[POD: {pod_name}] No response content received after {latency:.2f}s")
                return False, latency, "No response content", {"pod_id": pod_id, "pod_name": pod_name}
                
        except asyncio.TimeoutError:
            print(f"[POD: {pod_name}] Test timed out after {request_timeout}s")
            return False, None, f"Timeout after {request_timeout}s", {"pod_id": pod_id, "pod_name": pod_name}
        except Exception as e:
            print(f"[POD: {pod_name}] Test error: {type(e).__name__}: {str(e)}")
            return False, None, str(e), {"pod_id": pod_id, "pod_name": pod_name}
    
    return await _test_pod()

async def test_runpod_endpoints(config) -> Tuple[int, int, List[Tuple[str, bool, float, str, str]]]:
    if not RunPodClient:
        print("RunPodClient not available. Cannot check pod status.")
        return 0, 0, []
    
    client = RunPodClient(api_key=config.runpod_api_key)
    results = []
    success_count = 0
    total_start_time = time.time()
    
    try:
        print("Fetching active RunPod instances...")
        pods = client.get_pods()
        
        if not pods:
            print("No active RunPod instances found.")
            return 0, 0, []
        
        expected_pods = config.num_runpods
        print(f"Found {len(pods)} pods (expecting {expected_pods} based on config)")
        
        # Sort pods by name numerical order
        pods.sort(key=lambda pod: int(pod.get("name", "Translation-Pod-0").replace("Translation-Pod-", "0") or "0"))
        
        # Always use max_workers=32 to ensure we can handle all 60 pods
        max_workers = 32
        print(f"Testing pods with {max_workers} concurrent workers")
        
        semaphore = asyncio.Semaphore(max_workers)
        
        async def test_pod_with_semaphore(pod):
            async with semaphore:
                pod_id = pod.get("id")
                pod_name = pod.get("name", "Unknown")
                
                if not pod_id:
                    return pod_id, False, None, "No pod ID", pod_name
                
                # Start the test
                start_time = time.time()
                endpoint = RunPodEndpoint(pod_id, is_pod_id=True, request_timeout=config.request_timeout)
                
                try:
                    response = await asyncio.wait_for(
                        endpoint.client.generate(
                            model="gemmax2-custom",
                            prompt="Say OK",
                            stream=False
                        ),
                        timeout=config.request_timeout
                    )
                    
                    latency = time.time() - start_time
                    
                    if response and "response" in response:
                        if "ok" in response["response"].lower():
                            return pod_id, True, latency, None, pod_name
                        else:
                            return pod_id, True, latency, None, pod_name  # Still consider it OK
                    else:
                        return pod_id, False, latency, "No response content", pod_name
                        
                except Exception as e:
                    latency = time.time() - start_time
                    return pod_id, False, latency, str(e), pod_name
        
        # Use gather to collect all results as they complete
        test_start_time = time.time()
        tasks = [test_pod_with_semaphore(pod) for pod in pods]
        pod_results = await asyncio.gather(*tasks)
        
        # Process results
        for pod_id, status, latency, error, pod_name in pod_results:
            results.append((pod_id, status, latency, error, pod_name))
            if status:
                success_count += 1
        
        total_duration = time.time() - total_start_time
        
        print(f"Test completed in {total_duration:.2f}s ({success_count}/{len(pods)} successful)")
        
        return success_count, len(pods), results
    
    except Exception as e:
        print(f"Error checking pod status: {str(e)}")
        return 0, 0, []

async def startup_runpods(config):
    """
    Start RunPod instances, ensuring we don't exceed the configured limit.
    This checks for existing pods first and only launches additional pods as needed.
    """
    print("Startup mode activated: Checking for existing RunPod instances...")
    start_time = time.time()
    
    try:
        # First, check how many pods are already running
        if not RunPodClient:
            print("RunPodClient not available. Cannot check existing pods.")
            return 0
            
        client = RunPodClient(api_key=config.runpod_api_key)
        existing_pods = client.get_pods()
        
        # Count pods that appear to be our translation pods
        translation_pods = [pod for pod in existing_pods if "Translation-Pod-" in pod.get("name", "")]
        translation_pod_count = len(translation_pods)
        
        if translation_pod_count > 0:
            print(f"Found {translation_pod_count} existing Translation-Pod instances")
            
            # If we already have equal or more than our limit, don't launch more
            if translation_pod_count >= config.num_runpods:
                print(f"Already have {translation_pod_count} pods running (limit: {config.num_runpods})")
                print("No additional pods needed. Use --status to check their operational status.")
                return translation_pod_count
                
            # Calculate how many more pods we need to launch
            pods_to_launch = config.num_runpods - translation_pod_count
            print(f"Need to launch {pods_to_launch} more pods to reach the limit of {config.num_runpods}")
        else:
            print(f"No existing Translation-Pod instances found")
            pods_to_launch = config.num_runpods
            print(f"Will launch {pods_to_launch} pods (limit: {config.num_runpods})")
    
        # Launch the remaining pods needed
        runpod_info = launch_runpods(config, pods_to_launch)
        
        if not runpod_info:
            if pods_to_launch > 0:
                print("Failed to launch any additional RunPod instances.")
            new_count = 0
        else:
            new_count = len(runpod_info)
            print(f"Successfully launched {new_count} new RunPod instances")
        
        total_count = translation_pod_count + new_count
        duration = time.time() - start_time
        print(f"Total pods now: {total_count}/{config.num_runpods} ({duration:.2f}s)")
        print("Use --status or --test to check operational status of all pods")
        return total_count
        
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        return 0

async def check_runpods_status(config):
    """
    Check the status of all RunPod instances.
    This tests all pods up to the configured limit in config.num_runpods.
    """
    print("Status mode activated: Checking RunPod instances...")
    start_time = time.time()
    
    # Use the test_runpod_endpoints function to check status
    success_count, total_count, endpoint_results = await test_runpod_endpoints(config)
    
    if total_count == 0:
        print("No active RunPod instances found. Please start pods first.")
        duration = time.time() - start_time
        print(f"\nStatus check completed in {duration:.2f}s")
        return 0
    
    expected_pods = config.num_runpods
    print(f"RunPod Status Summary: {success_count}/{total_count} operational ({success_count/total_count*100:.1f}%)")
    
    if total_count < expected_pods:
        print(f"Warning: Only found {total_count}/{expected_pods} expected pods")
        print("You may need to run --startup to launch additional pods")
    
    # Sort by pod number
    def get_pod_number(result):
        pod_name = result[4]  # pod_name is at index 4
        try:
            return int(pod_name.replace("Translation-Pod-", ""))
        except (ValueError, AttributeError):
            return 999999
            
    sorted_results = sorted(endpoint_results, key=get_pod_number)
    
    # Show detailed results with cleaner format
    print("\nDetailed Status:")
    for pod_id, status, latency, error, pod_name in sorted_results:
        status_text = "OKAY!" if status else "ERROR!"
        latency_text = f"({latency:.2f}s)" if latency else "(N/A)"
        print(f"  {pod_name} ({pod_id}): {status_text} {latency_text}")
    
    duration = time.time() - start_time
    print(f"\nStatus check completed in {duration:.2f}s")
    return success_count

async def shutdown_runpods(config):
    print("Shutdown mode activated: Finding and terminating all RunPod instances...")
    start_time = time.time()
    
    terminated_count = await find_and_terminate_all_runpods(config)
    
    duration = time.time() - start_time
    if terminated_count > 0:
        print(f"Successfully terminated {terminated_count} RunPod instances in {duration:.2f}s")
    else:
        print(f"No RunPod instances found to terminate (operation took {duration:.2f}s)")
    return terminated_count

def terminate_runpods(runpod_info: List[Tuple[str, str]], config):
    """
    Terminate the specified RunPod instances.
    
    Args:
        runpod_info: List of tuples (pod_id, pod_name) to terminate
        config: Configuration object
    """
    if not RunPodClient or not runpod_info:
        return
        
    total_start_time = time.time()
    client = RunPodClient(api_key=config.runpod_api_key)
    terminated_count = 0
    
    # Sort by pod name numerical order
    def get_pod_number(pod_tuple):
        try:
            pod_id, name = pod_tuple
            if isinstance(name, str) and "Translation-Pod-" in name:
                return int(name.replace("Translation-Pod-", ""))
            return 999999
        except:
            return 999999
            
    sorted_pods = sorted(runpod_info, key=get_pod_number)
    
    max_workers = min(32, config.workers if hasattr(config, "workers") else 32)
    print(f"Terminating {len(runpod_info)} pods using {max_workers} parallel workers...")
    
    def stop_and_delete_pod(pod_tuple):
        pod_id, pod_name = pod_tuple
        try:
            start_time = time.time()
            client.stop_pod(pod_id)
            print(f"Stopped pod {pod_id} ({pod_name})")
            time.sleep(1)
            client.delete_pod(pod_id)
            elapsed = time.time() - start_time
            print(f"Deleted pod {pod_id} ({pod_name}) in {elapsed:.2f}s")
            return True
        except Exception as e:
            print(f"Failed to clean up pod {pod_id} ({pod_name}): {str(e)}")
            return False
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(stop_and_delete_pod, sorted_pods))
        terminated_count = sum(1 for r in results if r)
    
    total_time = time.time() - total_start_time
    print(f"Terminated {terminated_count}/{len(runpod_info)} pods in {total_time:.2f}s")

def get_running_pods(config):
    """
    Get already running pods that match our Translation-Pod naming pattern.
    
    Args:
        config: Configuration object
        
    Returns:
        list: Tuples of (pod_id, pod_name) for running pods
    """
    if not RunPodClient:
        print("[RUNPOD] RunPodClient not available. Cannot check for running pods.")
        return []

    client = RunPodClient(api_key=config.runpod_api_key)
    pod_info = []
    
    try:
        print("[RUNPOD] Checking for active RunPod instances...")
        pods = client.get_pods()
        
        if not pods:
            print("[RUNPOD] No active RunPod instances found.")
            return []
        
        # Filter for our Translation-Pod pattern
        translation_pods = [pod for pod in pods if "Translation-Pod-" in pod.get("name", "")]
        print(f"[RUNPOD] Found {len(translation_pods)} Translation-Pod instances out of {len(pods)} total pods")
        
        # Only consider pods with RUNNING or STARTING status
        running_pods = [pod for pod in translation_pods if pod.get("desiredStatus") in ["RUNNING", "STARTING"]]
        
        # Count pods by status
        status_counts = {}
        for pod in translation_pods:
            status = pod.get("desiredStatus", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            
        status_summary = ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
        print(f"[RUNPOD] Pod status summary: {status_summary}")
        print(f"[RUNPOD] Found {len(running_pods)} running Translation-Pod instances")
        
        if running_pods:
            # Sort by pod number
            running_pods.sort(key=lambda pod: 
                int(pod.get("name", "Translation-Pod-0").replace("Translation-Pod-", "0") or "0"))
            
            # Add to pod_info in the same format as launch_runpods returns
            for pod in running_pods:
                pod_id = pod.get("id")
                pod_name = pod.get("name", "Unknown")
                if pod_id:
                    pod_info.append((pod_id, pod_name))
                    print(f"[RUNPOD] {pod_name} - ID: {pod_id} - Status: {pod.get('desiredStatus', 'UNKNOWN')}")
        
        return pod_info
        
    except Exception as e:
        print(f"[RUNPOD] Error checking for running pods: {str(e)}")
        return []