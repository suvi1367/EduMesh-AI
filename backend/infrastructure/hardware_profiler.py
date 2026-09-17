import platform
import os
import psutil
import subprocess


def _get_cpu_name() -> str:
    """Attempts cross-platform CPU model name detection."""
    try:
        if platform.system() == "Windows":
            # Fast registry/wmic check on Windows
            output = subprocess.check_output(
                ["wmic", "cpu", "get", "name"],
                stderr=subprocess.DEVNULL,
                text=True
            )
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            if len(lines) > 1:
                return lines[1]
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        elif platform.system() == "Darwin":
            output = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                stderr=subprocess.DEVNULL,
                text=True
            )
            return output.strip()
    except Exception:
        pass
    return platform.processor() or "Generic CPU"


def _detect_gpu_info() -> dict:
    """
    Safely detects GPU details without crashing if unavailable or unconfigured.
    Returns dict with gpu_available, gpu_name, and vram_gb.
    """
    gpu_info = {
        "gpu_available": False,
        "gpu_name": None,
        "vram_gb": None
    }

    # 1. Try PyTorch if installed
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info["gpu_available"] = True
            gpu_info["gpu_name"] = torch.cuda.get_device_name(0)
            gpu_info["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
            return gpu_info
    except Exception:
        pass

    # 2. Try nvidia-smi command
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        parts = [p.strip() for p in output.splitlines()[0].split(",")]
        if len(parts) >= 2:
            gpu_info["gpu_available"] = True
            gpu_info["gpu_name"] = parts[0]
            gpu_info["vram_gb"] = round(float(parts[1]) / 1024.0, 2)
            return gpu_info
    except Exception:
        pass

    # 3. Try Windows wmic path
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                ["wmic", "path", "win32_VideoController", "get", "name,adapterram"],
                stderr=subprocess.DEVNULL,
                text=True
            )
            lines = [l.strip() for l in output.splitlines() if l.strip()]
            if len(lines) > 1:
                # Ignore basic display adapters if needed
                for line in lines[1:]:
                    if not any(ig in line.lower() for ig in ["basic display", "software renderer"]):
                        parts = line.rsplit(maxsplit=1)
                        name = parts[0].strip()
                        vram = None
                        if len(parts) > 1 and parts[1].isdigit():
                            bytes_vram = int(parts[1])
                            if bytes_vram > 0:
                                vram = round(bytes_vram / (1024 ** 3), 2)
                        gpu_info["gpu_available"] = True
                        gpu_info["gpu_name"] = name
                        gpu_info["vram_gb"] = vram
                        return gpu_info
        except Exception:
            pass

    return gpu_info


def get_hardware_profile() -> dict:
    """
    Returns normalized structured hardware profiling JSON-compatible dictionary.
    """
    # RAM profile
    mem = psutil.virtual_memory()
    ram_gb = round(mem.total / (1024 ** 3), 2)
    available_ram_gb = round(mem.available / (1024 ** 3), 2)

    # CPU profile
    cpu_cores = psutil.cpu_count(logical=False) or 1
    cpu_threads = psutil.cpu_count(logical=True) or cpu_cores
    cpu_name = _get_cpu_name()
    cpu_freq_ghz = None
    try:
        freq = psutil.cpu_freq()
        if freq and freq.max > 0:
            cpu_freq_ghz = round(freq.max / 1000.0, 2)
        elif freq and freq.current > 0:
            cpu_freq_ghz = round(freq.current / 1000.0, 2)
    except Exception:
        pass

    # Storage profile (root directory / current workspace drive)
    root_path = os.path.abspath(os.sep)
    disk = psutil.disk_usage(root_path)
    storage_total_gb = round(disk.total / (1024 ** 3), 2)
    storage_available_gb = round(disk.free / (1024 ** 3), 2)

    # GPU profile
    gpu_info = _detect_gpu_info()

    return {
        "ram_gb": ram_gb,
        "available_ram_gb": available_ram_gb,
        "cpu_name": cpu_name,
        "cpu_cores": cpu_cores,
        "cpu_threads": cpu_threads,
        "cpu_freq_ghz": cpu_freq_ghz,
        "storage_total_gb": storage_total_gb,
        "storage_available_gb": storage_available_gb,
        "gpu_available": gpu_info["gpu_available"],
        "gpu_name": gpu_info["gpu_name"],
        "vram_gb": gpu_info["vram_gb"],
        "platform": platform.system()
    }
