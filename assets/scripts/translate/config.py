import os
import time
import yaml
from typing import Dict, List

def load_config(config_path: str) -> Dict:
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return {}
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config file {config_path}: {str(e)}")
        return {}

class Config:
    def __init__(self, config_path: str):
        # Default values
        self.dataset_name = "DataTonic/dark_thoughts_case_study_reason"
        self.output_dir = "translated_dataset"
        self.state_file = "translation_state.json"
        self.batch_size = 5
        self.num_runpods = 60
        self.checkpoint_interval = 20
        self.startup_delay = 120
        self.max_retries = 6
        self.request_timeout = 30
        self.runpod_api_key = None
        self.hf_token = None
        
        # Default source and target languages
        self.source_languages = ["English", "Chinese"]
        self.target_languages = [
            "Arabic", "Bengali", "Czech", "German", "English", "Spanish", "Persian", "French",
            "Hebrew", "Hindi", "Indonesian", "Italian", "Japanese", "Khmer", "Korean", "Lao",
            "Malay", "Burmese", "Dutch", "Polish", "Portuguese", "Russian", "Thai", "Tagalog",
            "Turkish", "Urdu", "Vietnamese", "Chinese"
        ]
        
        # For backward compatibility
        self.languages = self.target_languages
        
        # Load from file
        self._load_from_file(config_path)
        
    def _load_from_file(self, config_path: str):
        config_data = load_config(config_path)
        if not config_data:
            return
            
        # Map old config names to new names for backward compatibility
        if "offload_interval" in config_data:
            config_data["checkpoint_interval"] = config_data.pop("offload_interval")
            
        if "pod_startup_delay" in config_data:
            config_data["startup_delay"] = config_data.pop("pod_startup_delay")
            
        # Update attributes from config file
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Handle custom fields from YAML
        if "source-language" in config_data:
            self.source_languages = config_data["source-language"]
        
        if "target-languages" in config_data:
            self.target_languages = config_data["target-languages"]
            # For backward compatibility
            self.languages = self.target_languages
                
        # Fallback to environment variables for sensitive information
        if not self.runpod_api_key:
            self.runpod_api_key = os.getenv("RUNPOD_API_KEY")
        if not self.hf_token:
            self.hf_token = os.getenv("HF_TOKEN", "")
            
    def setup_run_dir(self) -> Dict[str, str]:
        run_id = str(int(time.time()))
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
        data_dir = os.path.join(project_root, "data")
        run_dir = os.path.join(data_dir, run_id)
        output_dir = os.path.join(run_dir, "translated_dataset")
        state_file = os.path.join(run_dir, "translation_state.json")
        temp_dir = os.path.join(run_dir, "temp")
        
        # Create directories
        for directory in [data_dir, run_dir, output_dir, temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print(f"Created run directory with ID: {run_id}")
        
        return {
            "run_id": run_id,
            "project_root": project_root,
            "data_dir": data_dir,
            "run_dir": run_dir,
            "output_dir": output_dir,
            "temp_dir": temp_dir,
            "state_file": state_file
        }
