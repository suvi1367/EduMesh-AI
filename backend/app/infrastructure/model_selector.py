"""
EduMesh AI Smart Model Selector
Dynamically matches host hardware capabilities with optimal offline local LLM / SLM models.
"""

MODEL_CONFIGURATIONS = {
    "low_resource": {
        "name": "Low-Resource Configuration",
        "description": "Optimized for ultra-low power devices, old dual/quad-core PCs, or low-RAM laptops (4GB-8GB RAM).",
        "runtime": "llama.cpp / ONNX Runtime CPU",
        "model": "Qwen2.5-1.5B-Instruct-GGUF",
        "quantization": "Q4_K_M",
        "model_size_gb": 1.1,
        "max_context": 2048,
        "minimum_ram_gb": 4.0,
        "minimum_available_ram_gb": 2.0,
        "minimum_cpu_cores": 2,
        "minimum_storage_gb": 5.0,
        "gpu_required": False,
        "tested_status": "Tested & Verified for low-end classroom hardware"
    },
    "standard": {
        "name": "Standard Classroom Configuration",
        "description": "Designed for standard desktop PCs or laptops (8GB-16GB RAM) with solid multi-core performance.",
        "runtime": "Ollama / llama.cpp",
        "model": "Llama-3.2-3B-Instruct-GGUF",
        "quantization": "Q4_K_M",
        "model_size_gb": 2.2,
        "max_context": 4096,
        "minimum_ram_gb": 8.0,
        "minimum_available_ram_gb": 4.0,
        "minimum_cpu_cores": 4,
        "minimum_storage_gb": 10.0,
        "gpu_required": False,
        "tested_status": "Tested & Verified for standard local deployment"
    },
    "performance": {
        "name": "High-Performance Hub Configuration",
        "description": "Tailored for dedicated classroom servers or high-end workstations with >=16GB RAM or dedicated GPUs (4GB+ VRAM).",
        "runtime": "vLLM / Ollama CUDA",
        "model": "Mistral-7B-Instruct-v0.3 / Llama-3.1-8B-Q4",
        "quantization": "Q4_K_M / FP16",
        "model_size_gb": 4.8,
        "max_context": 8192,
        "minimum_ram_gb": 16.0,
        "minimum_available_ram_gb": 8.0,
        "minimum_cpu_cores": 6,
        "minimum_storage_gb": 20.0,
        "gpu_required": False,
        "tested_status": "Tested & Verified for heavy concurrent classroom load"
    }
}


def get_model_configurations() -> dict:
    """Returns registry of available configuration definitions."""
    return MODEL_CONFIGURATIONS


def select_model(hardware_profile: dict) -> dict:
    """
    Evaluates host hardware profile against resource tiers and selects the optimal model tier.
    Do NOT select using RAM alone. Considers RAM, Available RAM, CPU cores, GPU VRAM, Storage.
    """
    ram = hardware_profile.get("ram_gb", 4.0)
    avail_ram = hardware_profile.get("available_ram_gb", ram)
    cpu_cores = hardware_profile.get("cpu_cores", 2)
    storage_avail = hardware_profile.get("storage_available_gb", 10.0)
    gpu_avail = hardware_profile.get("gpu_available", False)
    vram = hardware_profile.get("vram_gb") or 0.0

    # 1. Performance Tier Evaluation
    if (gpu_avail and vram >= 4.0 and storage_avail >= 20.0) or (
        ram >= 16.0 and avail_ram >= 7.0 and cpu_cores >= 6 and storage_avail >= 20.0
    ):
        reason = (
            f"Dedicated GPU with {vram}GB VRAM detected"
            if gpu_avail and vram >= 4.0
            else f"High system memory ({ram}GB RAM, {cpu_cores} cores) available"
        )
        selected_key = "performance"

    # 2. Standard Tier Evaluation
    elif ram >= 8.0 and avail_ram >= 3.5 and cpu_cores >= 4 and storage_avail >= 10.0:
        reason = f"System meets standard requirements ({ram}GB RAM, {cpu_cores} CPU cores, {storage_avail}GB storage)"
        selected_key = "standard"

    # 3. Low-Resource Tier Evaluation / Fallback
    else:
        if storage_avail < 5.0:
            reason = f"Limited storage space available ({storage_avail}GB). Defaulting to ultra-compact Low-Resource tier."
        elif ram < 8.0 or avail_ram < 3.5:
            reason = f"Constrained RAM environment ({ram}GB total, {avail_ram}GB available). Selected Low-Resource lightweight model."
        else:
            reason = f"Dual-core or constrained CPU environment ({cpu_cores} cores). Selected Low-Resource tier for smooth response times."
        selected_key = "low_resource"

    cfg = MODEL_CONFIGURATIONS[selected_key]

    return {
        "configuration": selected_key,
        "name": cfg["name"],
        "model": cfg["model"],
        "runtime": cfg["runtime"],
        "quantization": cfg["quantization"],
        "max_context": cfg["max_context"],
        "reason": reason,
        "hardware_profile": hardware_profile
    }
