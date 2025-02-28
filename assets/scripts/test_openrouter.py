import sys
import time
import asyncio
from openai import AsyncOpenAI
from tenacity import retry, wait_random, stop_after_attempt, retry_if_exception_type

API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1"
MAX_WORKERS = 10
MAX_TOKENS = 10
TEST_TIMEOUT = 30
MAX_RETRIES = 5
SYSTEM_MESSAGE = "You are a helpful assistant responding to the user's question."
USER_MESSAGE = "What is the meaning of life?"

MODELS = {
    "dolphin": "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
    "mistral": "mistralai/mistral-7b-instruct",
    "llama3": "meta-llama/llama-3-8b-instruct:free",
    "gemini-flash": "google/gemini-2.0-flash-lite-preview-02-05:free",
    "gemini-pro": "google/gemini-2.0-pro-exp-02-05:free",
    "mistral-small": "mistralai/mistral-small-24b-instruct-2501:free",
    "deepseek-r1": "deepseek/deepseek-r1-distill-llama-70b:free",
    "rogue-rose": "sophosympatheia/rogue-rose-103b-v0.2:free",
    "deepseek-chat": "deepseek/deepseek-chat:free",
    "nemotron-70b": "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "phi-3-mini": "microsoft/phi-3-mini-128k-instruct:free",
    "phi-3-medium": "microsoft/phi-3-medium-128k-instruct:free",
    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct:free"
}

def log(message):
    print(f"[{time.strftime('%X')}] {message}")

def truncate(text, max_length=50):
    return text if len(text) <= max_length else f"{text[:max_length]}..."

class EmptyContentError(Exception):
    pass

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_random(min=1, max=3),
    retry=retry_if_exception_type(EmptyContentError),
    reraise=True
)
async def test_model(name, model_id, semaphore):
    async with semaphore:
        retry_count = 0
        log(f"Testing model: {name}")
        start_time = time.time()
        
        try:
            client = AsyncOpenAI(
                base_url=BASE_URL,
                api_key=API_KEY,
                default_headers={
                    "HTTP-Referer": "https://github.com/MultiTonic/thinking-dataset",
                    "X-Title": "Thinking Dataset"
                }
            )
            
            try:
                async with asyncio.timeout(TEST_TIMEOUT):
                    response = await client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": SYSTEM_MESSAGE},
                            {"role": "user", "content": USER_MESSAGE}
                        ],
                        max_tokens=MAX_TOKENS,
                        temperature=1,
                        stream=False
                    )
                    
                    elapsed = time.time() - start_time
                    
                    if not response or not response.choices or not response.choices[0].message:
                        raise EmptyContentError(f"Model {name} returned empty response structure")
                    
                    content = response.choices[0].message.content
                    if not content or content.strip() == "":
                        raise EmptyContentError(f"Model {name} returned empty content")
                        
                    tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else None
                    
                    return {
                        "success": True,
                        "model": name,
                        "time": elapsed,
                        "content": content,
                        "tokens": tokens
                    }
                    
            except EmptyContentError as e:
                retry_count += 1
                elapsed = time.time() - start_time
                log(f"Empty content from {name} (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
                raise
                
            except (asyncio.TimeoutError, Exception) as e:
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "model": name,
                    "time": elapsed,
                    "error": str(e)
                }
                
        except Exception as e:
            elapsed = time.time() - start_time
            if not isinstance(e, EmptyContentError) or retry_count >= MAX_RETRIES:
                return {
                    "success": False,
                    "model": name,
                    "time": elapsed,
                    "error": str(e)
                }
            raise

async def test_all_models():
    log("OpenRouter API Model Test Tool")
    log(f"System message: \"{SYSTEM_MESSAGE}\"")
    log(f"User message: \"{USER_MESSAGE}\"")
    log(f"Max tokens: {MAX_TOKENS}")
    log(f"Max retries: {MAX_RETRIES}")
    log(f"Testing {len(MODELS)} models with {MAX_WORKERS} workers...")
    
    semaphore = asyncio.Semaphore(MAX_WORKERS)
    tasks = [test_model(name, model_id, semaphore) for name, model_id in MODELS.items()]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append({
                "success": False,
                "model": "unknown",
                "time": 0,
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    log("\n" + "=" * 80)
    log(" MODEL TEST RESULTS ".center(80, "="))
    log("=" * 80)
    
    success_count = sum(1 for r in processed_results if r.get("success", False))
    log(f"Models tested: {len(processed_results)}")
    log(f"Successful: {success_count}/{len(processed_results)}")
    log(f"Total time: {total_time:.2f}s")
    log("-" * 80)
    
    processed_results.sort(key=lambda r: r.get("model", ""))
    
    log(f"{'MODEL':<16} {'STATUS':<10} {'TIME':<8} {'TOKENS':<8} {'RESPONSE/ERROR'}")
    log("-" * 80)
    
    for r in processed_results:
        model = r.get("model", "unknown")
        status = "SUCCESS" if r.get("success", False) else "FAILED"
        time_str = f"{r.get('time', 0):.2f}s"
        tokens = r.get("tokens", "-")
        
        if r.get("success", False):
            details = truncate(r.get("content", ""))
        else:
            details = truncate(r.get("error", "Unknown error"))
            
        log(f"{model:<16} {status:<10} {time_str:<8} {tokens:<8} {details}")
    
    log("=" * 80)
    
    return success_count

if __name__ == "__main__":
    try:
        success_count = asyncio.run(test_all_models())
        sys.exit(0 if success_count > 0 else 1)
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
