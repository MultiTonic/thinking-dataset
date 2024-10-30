# scripts\utilities\runpod_utils.py

import torch
import psutil
import os
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class GPUStats:
    total_memory: int
    used_memory: int
    free_memory: int

def get_gpu_stats() -> Dict[int, GPUStats]:
    """Get GPU memory statistics for all available GPUs."""
    gpu_stats = {}
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            total = torch.cuda.get_device_properties(i).total_memory
            used = torch.cuda.memory_allocated(i)
            free = total - used
            gpu_stats[i] = GPUStats(total, used, free)
    return gpu_stats

def get_optimal_thread_count() -> int:
    """Calculate optimal thread count based on CPU cores."""
    return max(1, psutil.cpu_count(logical=False))

def calculate_container_configs(total_memory: int, num_containers: int) -> List[Dict]:
    """Calculate optimal container configurations based on available GPU memory."""
    memory_per_container = total_memory // num_containers
    configs = []
    
    # Different quantization options for Yi model
    quantization_options = [
        ("q4_k_m", 0.25),  # Q4_K_M uses approximately 25% of original model size
        ("q4_0", 0.23),    # Q4_0 uses approximately 23% of original model size
        ("q4_1", 0.24)     # Q4_1 uses approximately 24% of original model size
    ]
    
    for i in range(num_containers):
        quant_type, mem_factor = quantization_options[i % len(quantization_options)]
        configs.append({
            "model_name": f"yi:6b-{quant_type}",
            "quantization": quant_type,
            "num_ctx": min(8192, int(memory_per_container * mem_factor / 6)),  # Context size based on available memory
            "num_batch": 512,
            "num_thread": get_optimal_thread_count() // num_containers
        })
    
    return configs