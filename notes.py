
# Custom TestContainer Ollama LLM Implementation
class TestContainerOllamaLLM:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.ollama_home = Path.home() / ".ollama"
        self._container = None

    def load(self):
        """Initialize the Ollama container"""
        self._container = OllamaContainer(ollama_home=self.ollama_home)
        self._container.start()
        
        # Check if model exists and pull if necessary
        models = self._container.list_models()
        if self.model_name not in [model["name"] for model in models]:
            self._container.pull_model(self.model_name)

    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> List[str]:
        """Async generation method compatible with the pipeline"""
        if not self._container:
            raise RuntimeError("Container not initialized. Call load() first.")

        try:
            endpoint = self._container.get_endpoint()
            response = requests.post(
                f"{endpoint}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    **kwargs
                }
            )
            response.raise_for_status()
            result = response.json()
            return [result["message"]["content"]]
        except Exception as e:
            logging.error(f"Generation error: {e}")
            return [""]

    def __del__(self):
        """Cleanup the container"""
        if self._container:
            self._container.stop()
