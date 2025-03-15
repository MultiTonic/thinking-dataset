import asyncio
import time
from typing import List, Tuple

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

def launch_runpods(config):
    if not RunPodClient:
        print("RunPodClient not available. Running locally.")
        return []

    client = RunPodClient(api_key=config.runpod_api_key)
    pod_ids = []

    try:
        print("Fetching available templates...")
        templates = client.get_templates()
        ollama_template_id = None
        for template in templates:
            if "ollama/ollama" in template.get("imageName", ""):
                ollama_template_id = template["id"]
                print(f"Found existing Ollama template: {template['name']} (ID: {ollama_template_id})")
                break

        if not ollama_template_id:
            print("No Ollama template found, creating a new one...")
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
                "ollama serve & sleep 5 && "
                "echo 'FROM hf.co/mradermacher/GemmaX2-28-2B-v0.1-GGUF:Q8_0\n"
                "PARAMETER num_ctx 32768\n"
                "PARAMETER num_predict 32000\n"
                "PARAMETER num_gpu 99\n"
                "' > /tmp/Modelfile && "
                "ollama create gemmax2-custom -f /tmp/Modelfile && "
                "ollama run gemmax2-custom"
            ]
        }

        # Updated to use startup_delay instead of pod_startup_delay
        print(f"Launching {config.num_runpods} pods with A40 GPUs and Ollama setup...")
        for i in range(config.num_runpods):
            pod_name = f"Translation-Pod-{i+1}"
            print(f"Creating {pod_name}...")
            pod = client.create_pod_from_template(
                template_id=ollama_template_id,
                name=pod_name,
                additional_config=pod_config
            )
            pod_id = pod["id"]
            pod_ids.append((pod_id, pod_id))
            print(f"Created {pod_name} with ID: {pod_id}")
            client.start_pod(pod_id)
            print(f"Started {pod_name}")

        # Updated to use startup_delay instead of pod_startup_delay
        print(f"Waiting {config.startup_delay // 60} minutes before checking pod status...")
        time.sleep(config.startup_delay)

        running_pods = {}
        for attempt in range(1, config.max_retries + 1):
            print(f"\nStatus check attempt {attempt}/{config.max_retries} after {config.startup_delay // 60} minutes")
            all_running = True
            for pod_id, _ in pod_ids:
                if pod_id in running_pods:
                    continue
                pod_details = client.get_pod(pod_id, include_details=True)
                status = pod_details.get("desiredStatus", "UNKNOWN")
                print(f"Pod {pod_id}: Status - {status}")
                if status == "RUNNING":
                    running_pods[pod_id] = pod_id
                else:
                    all_running = False
            if all_running:
                print(f"All {config.num_runpods} pods are running!")
                break
            if attempt < config.max_retries:
                print(f"Retrying in {config.startup_delay // 60} minutes...")
                time.sleep(config.startup_delay)
            else:
                print(f"Maximum retries reached. Proceeding with {len(running_pods)}/{config.num_runpods} pods.")

        return list(running_pods.items())

    except Exception as e:
        print(f"Error launching pods: {str(e)}")
        return []

async def find_and_terminate_all_runpods(config) -> int:
    if not RunPodClient:
        print("RunPodClient not available. Cannot terminate pods.")
        return 0
    
    client = RunPodClient(api_key=config.runpod_api_key)
    terminated_count = 0
    
    try:
        print("Fetching all active RunPod instances...")
        pods = client.get_pods()
        
        if not pods:
            print("No active RunPod instances found.")
            return 0
        
        print(f"Found {len(pods)} RunPod instances.")
        
        for pod in pods:
            pod_id = pod.get("id")
            pod_name = pod.get("name", "Unnamed")
            status = pod.get("desiredStatus", "UNKNOWN")
            
            if not pod_id:
                continue
                
            print(f"Pod {pod_id} ({pod_name}) - Status: {status}")
            
            if status in ["RUNNING", "PENDING", "STOPPING"]:
                try:
                    print(f"Stopping pod {pod_id} ({pod_name})...")
                    client.stop_pod(pod_id)
                    await asyncio.sleep(2)  # Give API time to process
                    print(f"Deleting pod {pod_id} ({pod_name})...")
                    client.delete_pod(pod_id)
                    terminated_count += 1
                    print(f"Successfully terminated pod {pod_id} ({pod_name})")
                except Exception as e:
                    print(f"Failed to terminate pod {pod_id} ({pod_name}): {str(e)}")
    
    except Exception as e:
        print(f"Error while finding/terminating pods: {str(e)}")
    
    return terminated_count

def terminate_runpods(runpod_info: List[Tuple[str, str]], config):
    if not RunPodClient or not runpod_info:
        return
    client = RunPodClient(api_key=config.runpod_api_key)
    for pod_id, _ in runpod_info:
        try:
            client.stop_pod(pod_id)
            print(f"Stopped pod {pod_id}")
            time.sleep(2)
            client.delete_pod(pod_id)
            print(f"Deleted pod {pod_id}")
        except Exception as e:
            print(f"Failed to clean up pod {pod_id}: {str(e)}")

async def test_single_pod(pod_id: str, pod_name: str, max_retries: int = 3, request_timeout: int = 30) -> Tuple[bool, float, str]:
    retry_decorator = create_retry_decorator(max_retries)
    
    @retry_decorator
    async def _test_pod():
        try:
            print(f"Testing pod {pod_id} ({pod_name})...")
            endpoint = RunPodEndpoint(pod_id, is_pod_id=True, request_timeout=request_timeout)
            
            start_time = time.time()
            response = await asyncio.wait_for(
                endpoint.client.generate(
                    model="gemmax2-custom",
                    prompt="Say OK",
                    stream=False
                ),
                timeout=request_timeout
            )
            latency = time.time() - start_time
            
            if response and "response" in response:
                if "ok" in response["response"].lower():
                    return True, latency, None
                else:
                    return True, latency, f"Unexpected response: {response['response'][:20]}..."
            else:
                return False, latency, "No response content"
                
        except asyncio.TimeoutError:
            print(f"Pod {pod_id} ({pod_name}) test timed out after {request_timeout}s")
            return False, None, f"Timeout after {request_timeout}s"
        except Exception as e:
            print(f"Pod {pod_id} ({pod_name}) test error: {type(e).__name__}: {str(e)}")
            return False, None, str(e)
    
    return await _test_pod()

async def test_runpod_endpoints(config) -> Tuple[int, int, List[Tuple[str, bool, float, str]]]:
    if not RunPodClient:
        print("RunPodClient not available. Cannot check pod status.")
        return 0, 0, []
    
    client = RunPodClient(api_key=config.runpod_api_key)
    results = []
    success_count = 0
    
    try:
        print("Fetching all active RunPod instances...")
        pods = client.get_pods()
        
        if not pods:
            print("No active RunPod instances found.")
            return 0, 0, []
        
        print(f"Found {len(pods)} RunPod instances.")
        
        test_tasks = []
        for pod in pods:
            pod_id = pod.get("id")
            if not pod_id:
                continue
                
            test_tasks.append(test_single_pod(
                pod_id, 
                pod.get("name", "Unknown"), 
                config.max_retries,
                config.request_timeout
            ))
        
        if test_tasks:
            pod_results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            for i, result in enumerate(pod_results):
                pod_id = pods[i].get("id")
                if isinstance(result, Exception):
                    results.append((pod_id, False, None, str(result)))
                else:
                    status, latency, error = result
                    results.append((pod_id, status, latency, error))
                    if status:
                        success_count += 1
        
        return success_count, len(pods), results
    
    except Exception as e:
        print(f"Error checking pod status: {str(e)}")
        return 0, 0, []
    
async def startup_runpods(config):
    print("Startup mode activated: Launching RunPod instances...")
    
    # Just launch the pods but don't proceed with translation
    runpod_info = launch_runpods(config)
    
    if not runpod_info:
        print("Failed to launch any RunPod instances.")
        return 0
    
    print(f"Successfully launched {len(runpod_info)} RunPod instances")
    return len(runpod_info)

async def check_runpods_status(config):
    print("Status mode activated: Checking RunPod instances...")
    
    # Use the test_runpod_endpoints function to check status
    success_count, total_count, endpoint_results = await test_runpod_endpoints(config)
    
    print(f"RunPod Status Summary: {success_count}/{total_count} instances operational")
    
    # Show details for each endpoint
    for i, (pod_id, status, latency, error) in enumerate(endpoint_results):
        status_text = "OK!" if status else "Error"
        latency_text = f"{latency:.2f}s" if latency else "N/A"
        error_text = f" - Error: {error}" if error else ""
        print(f"  [{i+1}] Pod {pod_id}: {status_text} (Latency: {latency_text}){error_text}")
    
    return success_count

async def shutdown_runpods(config):
    print("Shutdown mode activated: Finding and terminating all RunPod instances...")
    terminated_count = await find_and_terminate_all_runpods(config)
    if terminated_count > 0:
        print(f"Successfully terminated {terminated_count} RunPod instances")
    else:
        print("No RunPod instances found to terminate")
    return terminated_count