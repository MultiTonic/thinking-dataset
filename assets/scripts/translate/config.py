import os
import time
import yaml
from typing import Dict, List

def load_config(config_path: str) -> Dict:
    print(f"[CONFIG] Loading configuration from: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"[CONFIG] Error: Config file not found at {config_path}")
        return {}
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"[CONFIG] Config loaded successfully")
        return config
    except Exception as e:
        print(f"[CONFIG] Error loading config file {config_path}: {str(e)}")
        return {}

class Config:
    def __init__(self, config_path: str):
        print(f"[CONFIG] Initializing configuration from: {config_path}")
        
        # Default values
        self.dataset_name = "DataTonic/dark_thoughts_case_study_reason"
        self.output_dir = "translated_dataset"
        self.state_file = "translation_state.json"
        self.batch_size = 5
        self.num_runpods = 60
        self.checkpoint_interval = 10
        self.startup_delay = 120
        self.max_retries = 6
        self.request_timeout = 30
        self.runpod_api_key = None
        self.hf_token = None
        
        # New default values
        self.max_records = 0  # 0 means process all records
        self.offset = 0
        
        # Default source and target languages
        self.source_languages = ["English", "Chinese"]
        self.target_languages = [
            "Arabic", "Bengali", "Czech", "German", "English", "Spanish", "Persian", "French",
            "Hebrew", "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean", "Lao",
            "Malay", "Burmese", "Dutch", "Polish", "Portuguese", "Russian", "Thai", "Tagalog",
            "Turkish", "Urdu", "Vietnamese", "Chinese"
        ]
        
        # Load from file
        self._load_from_file(config_path)
        
        # Log configuration summary
        self._log_config_summary()
        
    def _load_from_file(self, config_path: str):
        config_data = load_config(config_path)
        if not config_data:
            print("[CONFIG] Warning: No config data loaded, using defaults")
            return
        
        print(f"[CONFIG] Processing configuration options")    
        # Map old config names to new names for backward compatibility
        if "offload_interval" in config_data:
            print(f"[CONFIG] Converting legacy 'offload_interval' to 'checkpoint_interval'")
            config_data["checkpoint_interval"] = config_data.pop("offload_interval")
            
        if "pod_startup_delay" in config_data:
            print(f"[CONFIG] Converting legacy 'pod_startup_delay' to 'startup_delay'")
            config_data["startup_delay"] = config_data.pop("pod_startup_delay")
            
        # Update attributes from config file
        for key, value in config_data.items():
            if hasattr(self, key):
                print(f"[CONFIG] Setting {key} = {value}")
                setattr(self, key, value)
        
        # Handle custom fields from YAML
        if "source-language" in config_data:
            self.source_languages = config_data["source-language"]
            print(f"[CONFIG] Setting source languages: {', '.join(self.source_languages)}")
        
        if "target-languages" in config_data:
            self.target_languages = config_data["target-languages"]
            print(f"[CONFIG] Setting target languages: {', '.join(self.target_languages)}")
                
        # Fallback to environment variables for sensitive information
        if not self.runpod_api_key:
            self.runpod_api_key = os.getenv("RUNPOD_API_KEY")
            if self.runpod_api_key:
                print("[CONFIG] Using RunPod API key from environment variable")
                
        if not self.hf_token:
            self.hf_token = os.getenv("HF_TOKEN", "")
            if self.hf_token:
                print("[CONFIG] Using Hugging Face token from environment variable")
                
    def _log_config_summary(self):
        """Log a summary of the configuration"""
        print("\n[CONFIG] Configuration summary:")
        print(f"[CONFIG] - Dataset: {self.dataset_name}")
        print(f"[CONFIG] - Batch size: {self.batch_size}")
        print(f"[CONFIG] - Checkpoint interval: {self.checkpoint_interval}")
        print(f"[CONFIG] - Number of RunPods: {self.num_runpods}")
        print(f"[CONFIG] - Max retries: {self.max_retries}")
        print(f"[CONFIG] - Request timeout: {self.request_timeout}s")
        print(f"[CONFIG] - Startup delay: {self.startup_delay}s")
        print(f"[CONFIG] - Source languages: {len(self.source_languages)}")
        print(f"[CONFIG] - Target languages: {len(self.target_languages)}")
        print(f"[CONFIG] - Record limit: {'All' if self.max_records == 0 else self.max_records}")
        print(f"[CONFIG] - Record offset: {self.offset}")
        print(f"[CONFIG] - RunPod API key: {'Set' if self.runpod_api_key else 'Not set'}")
        print(f"[CONFIG] - HF token: {'Set' if self.hf_token else 'Not set'}")
        
    def setup_run_dir(self) -> Dict[str, str]:
        run_id = str(int(time.time()))
        print(f"[CONFIG] Setting up run directory with ID: {run_id}")
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
        data_dir = os.path.join(project_root, "data")
        run_dir = os.path.join(data_dir, run_id)
        output_dir = os.path.join(run_dir, "translated_dataset")
        state_file = os.path.join(run_dir, "translation_state.json")
        temp_dir = os.path.join(run_dir, "temp")
        
        # Create directories
        for directory in [data_dir, run_dir, output_dir, temp_dir]:
            os.makedirs(directory, exist_ok=True)
            print(f"[CONFIG] Created directory: {directory}")
        
        print(f"[CONFIG] Run directory setup complete with ID: {run_id}")
        
        return {
            "run_id": run_id,
            "project_root": project_root,
            "data_dir": data_dir,
            "run_dir": run_dir,
            "output_dir": output_dir,
            "temp_dir": temp_dir,
            "state_file": state_file
        }
