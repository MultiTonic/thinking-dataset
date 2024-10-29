
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



        # Initialize optimized vLLM
        # vllm_model = OptimizedVLLM(
        #     model="01-ai/Yi-6B", # Using Yi-6B model
        #     num_gpus=torch.cuda.device_count(),  # Use all available GPUs
        #     batch_size=32,
        #     max_model_len=8192,
        #     quantization="int8",  # Enable int8 quantization
        #     dtype="float16",      # Use float16 for better performance
        #     trust_remote_code=True,
        #     structured_output=None # No structured output needed for this case
        # )

# class TestContainerOllamaLLM(AsyncLLM):
#     """
#     TestContainers Ollama implementation that follows the Distilabel AsyncLLM interface.
#     """
#     model: str
#     host: Optional[RuntimeParameter[str]] = Field(
#         default=None, description="The host of the Ollama API."
#     )
#     timeout: RuntimeParameter[int] = Field(
#         default=120, description="The timeout for the Ollama API."
#     )
#     follow_redirects: bool = True
#     structured_output: Optional[RuntimeParameter[InstructorStructuredOutputType]] = Field(
#         default=None,
#         description="The structured output format to use across all the generations.",
#     )

#     _num_generations_param_supported = False
#     _container: Optional[OllamaContainer] = PrivateAttr(default=None)
#     _endpoint: Optional[str] = PrivateAttr(default=None)

#     def load(self) -> None:
#         """Initialize the Ollama container and setup the endpoint."""
#         super().load()
        
#         try:
#             ollama_home = Path.home() / ".ollama"
#             self._container = OllamaContainer(ollama_home=ollama_home)
#             self._container.start()
            
#             # Store the endpoint
#             self._endpoint = self._container.get_endpoint()
            
#             # Check if model exists and pull if necessary
#             models = self._container.list_models()
#             if self.model not in [model["name"] for model in models]:
#                 self._container.pull_model(self.model)
                
#         except Exception as e:
#             raise RuntimeError(f"Failed to initialize Ollama container: {e}")

#     @property
#     def model_name(self) -> str:
#         """Returns the model name used for the LLM."""
#         return self.model

#     async def agenerate(
#         self,
#         input: StandardInput,
#         format: str = "",
#         options: Union[Options, None] = None,
#         keep_alive: Union[bool, None] = None,
#     ) -> GenerateOutput:
#         """
#         Generates a response asynchronously using the TestContainers Ollama implementation.

#         Args:
#             input: the input to use for the generation.
#             format: the format to use for the generation.
#             options: the options to use for the generation.
#             keep_alive: whether to keep the connection alive.

#         Returns:
#             A list of strings as completion for the given input.
#         """
#         if not self._endpoint:
#             raise RuntimeError("Container not initialized. Call load() first.")

#         try:
#             response = requests.post(
#                 f"{self._endpoint}/api/chat",
#                 json={
#                     "model": self.model,
#                     "messages": input,
#                     "stream": False,
#                     "format": format,
#                     "options": options,
#                     "keep_alive": keep_alive
#                 }
#             )
#             response.raise_for_status()
#             result = response.json()
#             return [result["message"]["content"]]
#         except Exception as e:
#             self._logger.warning(
#                 f"⚠️ Error using Ollama client (model: '{self.model_name}'): {e}"
#             )
#             return [""]

#     def __del__(self):
#         """Cleanup the container on deletion."""
#         if self._container:
#             try:
#                 self._container.stop()
#             except Exception as e:
#                 logging.warning(f"Failed to stop Ollama container: {e}")