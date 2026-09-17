import pytest
from backend.infrastructure.hardware_profiler import get_hardware_profile, _detect_gpu_info


def test_hardware_profile_keys_and_types():
    profile = get_hardware_profile()
    assert isinstance(profile, dict)
    
    assert "ram_gb" in profile
    assert isinstance(profile["ram_gb"], float)
    assert profile["ram_gb"] > 0.0

    assert "available_ram_gb" in profile
    assert isinstance(profile["available_ram_gb"], float)
    assert profile["available_ram_gb"] <= profile["ram_gb"]

    assert "cpu_name" in profile
    assert isinstance(profile["cpu_name"], str)
    assert len(profile["cpu_name"]) > 0

    assert "cpu_cores" in profile
    assert isinstance(profile["cpu_cores"], int)
    assert profile["cpu_cores"] >= 1

    assert "cpu_threads" in profile
    assert isinstance(profile["cpu_threads"], int)
    assert profile["cpu_threads"] >= profile["cpu_cores"]

    assert "storage_total_gb" in profile
    assert isinstance(profile["storage_total_gb"], float)
    assert profile["storage_total_gb"] > 0.0

    assert "storage_available_gb" in profile
    assert isinstance(profile["storage_available_gb"], float)
    assert profile["storage_available_gb"] <= profile["storage_total_gb"]

    assert "gpu_available" in profile
    assert isinstance(profile["gpu_available"], bool)

    assert "platform" in profile
    assert profile["platform"] in ["Windows", "Linux", "Darwin"]


def test_missing_gpu_handling_never_crashes():
    gpu_info = _detect_gpu_info()
    assert isinstance(gpu_info, dict)
    assert "gpu_available" in gpu_info
    assert isinstance(gpu_info["gpu_available"], bool)
    if not gpu_info["gpu_available"]:
        assert gpu_info["gpu_name"] is None or isinstance(gpu_info["gpu_name"], str)
