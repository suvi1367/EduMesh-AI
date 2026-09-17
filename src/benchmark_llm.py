import time
import subprocess
import psutil

MODEL_NAME = "qwen2.5:1.5b"
TEST_PROMPT = "What is the SI unit of length? Answer in one sentence."

print(f"Benchmarking model: {MODEL_NAME}\n")

# Measure response time
start_time = time.time()

result = subprocess.run(
    ["ollama", "run", MODEL_NAME, TEST_PROMPT],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=60
)

end_time = time.time()
response_time = end_time - start_time

print(f"Response: {result.stdout.strip()}\n")

# Get accurate memory usage directly from Ollama
mem_result = subprocess.run(
    ["ollama", "ps"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

print(f"--- Benchmark Results ---")
print(f"Response time: {response_time:.2f} seconds")
print(f"\nOllama process info (from 'ollama ps'):")
print(mem_result.stdout.strip())

print(f"\nCPU cores available: {psutil.cpu_count()}")
print(f"Total system RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")