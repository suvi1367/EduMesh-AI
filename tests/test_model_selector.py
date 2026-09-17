import pytest
from backend.infrastructure.model_selector import select_model, get_model_configurations


def test_get_model_configurations():
    configs = get_model_configurations()
    assert "low_resource" in configs
    assert "standard" in configs
    assert "performance" in configs
    
    for key, cfg in configs.items():
        assert "model" in cfg
        assert "runtime" in cfg
        assert "quantization" in cfg
        assert "max_context" in cfg


def test_select_model_low_resource():
    low_profile = {
        "ram_gb": 4.0,
        "available_ram_gb": 2.1,
        "cpu_cores": 2,
        "storage_available_gb": 10.0,
        "gpu_available": False,
        "vram_gb": None,
        "platform": "Windows"
    }
    result = select_model(low_profile)
    assert result["configuration"] == "low_resource"
    assert "Qwen" in result["model"] or "low" in result["configuration"]


def test_select_model_standard():
    std_profile = {
        "ram_gb": 8.0,
        "available_ram_gb": 4.5,
        "cpu_cores": 4,
        "storage_available_gb": 25.0,
        "gpu_available": False,
        "vram_gb": None,
        "platform": "Windows"
    }
    result = select_model(std_profile)
    assert result["configuration"] == "standard"


def test_select_model_performance_gpu():
    perf_gpu_profile = {
        "ram_gb": 8.0,
        "available_ram_gb": 4.0,
        "cpu_cores": 4,
        "storage_available_gb": 50.0,
        "gpu_available": True,
        "vram_gb": 8.0,
        "platform": "Windows"
    }
    result = select_model(perf_gpu_profile)
    assert result["configuration"] == "performance"


def test_select_model_performance_high_ram():
    perf_ram_profile = {
        "ram_gb": 32.0,
        "available_ram_gb": 16.0,
        "cpu_cores": 8,
        "storage_available_gb": 100.0,
        "gpu_available": False,
        "vram_gb": None,
        "platform": "Linux"
    }
    result = select_model(perf_ram_profile)
    assert result["configuration"] == "performance"


def test_select_model_constrained_storage_fallback():
    constrained_profile = {
        "ram_gb": 16.0,
        "available_ram_gb": 10.0,
        "cpu_cores": 8,
        "storage_available_gb": 3.0,  # Insufficient storage
        "gpu_available": False,
        "vram_gb": None,
        "platform": "Windows"
    }
    result = select_model(constrained_profile)
    assert result["configuration"] == "low_resource"
