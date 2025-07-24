import subprocess
import re
import json
import os
from pathlib import Path
import ctypes
import time

def safe_run(cmd: str) -> str | None:
    """Run a shell command and return its stdout, or None if it fails.
    All stderr output is suppressed to keep logs clean."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

# 1. GPU

def get_nvlink_bond_map(topo_output: str) -> dict | None:
    bond_map = {}
    lines = topo_output.splitlines()
    gpu_labels = [line.split()[0] for line in lines if line.startswith("GPU")]

    for i, line in enumerate(lines):
        if not line.startswith("GPU"):
            continue
        entries = line.split()
        gpu_i = entries[0]
        bond_map.setdefault(gpu_i, [])
        for j, val in enumerate(entries[1:len(gpu_labels)+1]):
            if re.fullmatch(r"NV\d+", val):
                gpu_j = gpu_labels[j]
                if gpu_i < gpu_j:
                    bond_count = int(val[2:])
                    bond_map[gpu_i].append((gpu_j, bond_count))

    bond_map = {k: v for k, v in bond_map.items() if v}
    return bond_map or None

# --- GPU Summary Info ---

def get_gpu_info():
    gpu_names_output = safe_run("nvidia-smi --query-gpu=name --format=csv,noheader")
    gpu_names = gpu_names_output.splitlines() if gpu_names_output else []

    first_gpu_name = gpu_names[0] if gpu_names else ""
    gpu_type_match = re.search(r"(A\d{3}|H\d{3}|V\d{100}|RTX\s?\d{4}|L\d{2})", first_gpu_name.upper()) if first_gpu_name else None
    gpu_type = gpu_type_match.group(1) if gpu_type_match else "Unknown"

    vram_type_match = re.search(r"(HBM\d+|GDDR\d+)", first_gpu_name.upper()) if first_gpu_name else None
    vram_type = vram_type_match.group(1) if vram_type_match else "Unknown"

    gpu_vram_output = safe_run("nvidia-smi --query-gpu=memory.total --format=csv,noheader")
    gpu_vram = gpu_vram_output.splitlines()[0] if gpu_vram_output else "Unknown"

    topo_output = safe_run("nvidia-smi topo -m")
    if topo_output:
        nvlink = any("NV" in line for line in topo_output.splitlines())
        nvlink_bonds = get_nvlink_bond_map(topo_output)
    else:
        nvlink = False
        nvlink_bonds = None

    return {
        "GPU Type": gpu_type,
        "GPU VRAM": gpu_vram,
        "VRAM Type": vram_type,
        "GPU Count": len(gpu_names),
        "Has NVLink": nvlink,
        "NVLink Bonds": nvlink_bonds
    }

# 2. CPU

# PCIe Gen bandwidth table (GB/s per lane)
BANDWIDTH_PER_LANE_GB = {
    3: 1.0,
    4: 2.0,
    5: 4.0,
    6: 8.0
}

def run_cmd(cmd: str) -> str | None:
    """Wrapper around safe_run for legacy callers within this module."""
    return safe_run(cmd)

def parse_lscpu() -> dict:
    output = run_cmd("lscpu")
    if not output:
        return {
            "Chip Architecture": "Unknown",
            "CPU Model": "Unknown",
            "CPU Core Count": "Unknown",
            "CPU Thread Count": "Unknown"
        }

    info = {}
    sockets = cores_per_socket = threads_per_core = 1

    for line in output.splitlines():
        if "Architecture" in line:
            info["Chip Architecture"] = line.split(":")[1].strip()
        elif "Model name" in line:
            info["CPU Model"] = line.split(":")[1].strip()
        elif "Socket(s)" in line:
            sockets = int(line.split(":")[1].strip())
        elif "Core(s) per socket" in line:
            cores_per_socket = int(line.split(":")[1].strip())
        elif "Thread(s) per core" in line:
            threads_per_core = int(line.split(":")[1].strip())

    info["CPU Core Count"] = cores_per_socket * sockets
    info["CPU Thread Count"] = info["CPU Core Count"] * threads_per_core
    return info

def parse_os_release() -> str:
    with open("/etc/os-release") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip().strip('"')
    return "Unknown"

def parse_ram_size() -> str:
    output = run_cmd("free -h")
    if not output:
        return "Unknown"
    for line in output.splitlines():
        if line.lower().startswith("mem:"):
            total_ram = line.split()[1]
            return total_ram
    return "Unknown"

def parse_pcie_bandwidth() -> dict:
    try:
        output = subprocess.check_output(["nvidia-smi", "-q", "-i", "0"], text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"PCIe Gen": "Unknown", "Link Width": "Unknown", "Estimated BW (GB/s)": "Unknown"}

    gen_match = re.search(r"PCIe Generation\s+(?:Current|Max)\s+:\s+(\d+)", output)
    width_match = re.search(r"Link Width\s+(?:Current|Max)\s+:\s+(\d+)x", output)

    if gen_match and width_match:
        gen = int(gen_match.group(1))
        width = int(width_match.group(1))
        bw = BANDWIDTH_PER_LANE_GB.get(gen, 0) * width
        return {
            "PCIe Gen": gen,
            "Link Width": width,
            "Estimated BW (GB/s)": round(bw, 2)
        }

    return {"PCIe Gen": "Unknown", "Link Width": "Unknown", "Estimated BW (GB/s)": "Unknown"}

def get_cpu_info():
    cpu_info = parse_lscpu()
    cpu_info["Operating System"] = parse_os_release()
    cpu_info["RAM Size"] = parse_ram_size()

    pcie_info = parse_pcie_bandwidth()
    cpu_info.update(pcie_info)

    return cpu_info

# 3. Disk

def get_disk_info():
    pass

def get_nvme_mountpoint() -> str:
    """Return the first mountpoint of an NVMe device if any, else /tmp.
    The command here mirrors the one documented in README.md."""
    lsblk_out = safe_run("lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme")
    if not lsblk_out:
        return "/tmp"  # fallback if no NVMe is detected

    for line in lsblk_out.splitlines():
        parts = line.strip().split()
        # NAME HCTL SIZE MOUNTPOINT MODEL
        if len(parts) >= 4 and parts[3] != "":
            return parts[3]  # use first non-empty mountpoint
    return "/tmp"  # fallback if NVMe has no mountpoint


def run_fio_test(directory: str, mode: str) -> dict:
    """Run a single fio benchmark in either read or write mode against *directory*.
    Mirrors the commands in the README. Returns bandwidth and IOPS in MiB/s.
    """
    assert mode in ("read", "write")

    cmd = (
        f"fio --name={mode}test "
        f"--directory={directory} "
        f"--size=1G "
        f"--bs=32M "
        f"--rw={mode} "
        f"--ioengine=libaio "
        f"--direct=1 "
        f"--numjobs=4 "
        f"--iodepth=32 "
        f"--group_reporting"
    )

    output = safe_run(cmd)
    if not output:
        return {f"{mode.title()} Test": "Failed"}

    # Parse aggregated group line, e.g. "read: IOPS=128, BW=4096MiB/s (4294MB/s)"
    bw_match = re.search(r"BW=([0-9]+)MiB/s", output, flags=re.IGNORECASE)
    iops_match = re.search(r"IOPS=([0-9]+)", output, flags=re.IGNORECASE)

    # Custom field names per requirements
    prefix = "Disk -> CPU" if mode == "read" else "CPU -> Disk"

    return {
        f"{prefix} BW (MiB/s)": int(bw_match.group(1)) if bw_match else "Unknown",
        f"{prefix} IOPS": int(iops_match.group(1)) if iops_match else "Unknown"
    }


def run_disk_benchmark() -> dict:
    mountpoint = get_nvme_mountpoint()
    bench_dir = os.path.join(mountpoint, "fio-multifile")

    Path(bench_dir).mkdir(parents=True, exist_ok=True)

    result = {
        "NVMe Detected": mountpoint != "/tmp",
    }
    result.update(run_fio_test(bench_dir, "read"))  # Disk -> CPU
    result.update(run_fio_test(bench_dir, "write"))  # CPU -> Disk

    # Cleanup benchmark files & directory
    try:
        for f in Path(bench_dir).iterdir():
            f.unlink(missing_ok=True)  # type: ignore[arg-type]
        Path(bench_dir).rmdir()
    except OSError:
        pass

    return result


# ---------------- GPU <-> Disk Benchmark (GDS) -----------------


def run_gpu_disk_benchmark(mountpoint: str) -> dict:
    """Benchmark direct GPU ↔ Disk transfers using NVIDIA GDS (libcufile).
    Returns bandwidth in GB/s for both directions or a meaningful error string
    if prerequisites are missing (CUDA GPU, PyTorch, cufile)."""

    # Lazy imports to avoid hard dependency when library is absent.
    try:
        import torch  # type: ignore
        import cufile  # type: ignore
        from cufile import CuFile  # type: ignore
    except ImportError:
        return {
            "GPU -> Disk BW (GB/s)": "cufile or torch unavailable",
            "GPU -> Disk IOPS": "cufile or torch unavailable",
            "Disk -> GPU BW (GB/s)": "cufile or torch unavailable",
            "Disk -> GPU IOPS": "cufile or torch unavailable"
        }

    if not torch.cuda.is_available():
        return {
            "GPU -> Disk BW (GB/s)": "No CUDA GPU detected",
            "GPU -> Disk IOPS": "No CUDA GPU detected",
            "Disk -> GPU BW (GB/s)": "No CUDA GPU detected",
            "Disk -> GPU IOPS": "No CUDA GPU detected"
        }

    FILE_SIZE = 256 * 1024 * 1024  # 256 MB
    BLOCK_SIZE = 4 * 1024 * 1024   # 4 MB
    file_path = os.path.join(mountpoint, "gds_testfile.bin")
    USE_DIRECT_IO = True

    # Allocate a tensor on the first CUDA device
    tensor = torch.empty(FILE_SIZE // 4, dtype=torch.float32, device="cuda")
    dev_ptr = ctypes.c_void_p(tensor.data_ptr())

    # Register CuFile driver (no-op if already registered)
    _ = cufile.CuFileDriver()

    # Ensure file exists with the right size
    with open(file_path, "wb") as f:
        f.truncate(FILE_SIZE)

    results: dict[str, float | str] = {}

    # --- GPU -> Disk (write) ---
    try:
        with CuFile(file_path, "r+", use_direct_io=USE_DIRECT_IO) as f:
            torch.cuda.synchronize()
            start = time.perf_counter()
            f.write(dev_ptr, FILE_SIZE, file_offset=0, dev_offset=0)
            torch.cuda.synchronize()
            end = time.perf_counter()
            elapsed = end - start
            bw_gb_s = FILE_SIZE / elapsed / 1e9  # GB/s
            iops = (bw_gb_s * 1e9) / BLOCK_SIZE  # ops per second
            results["GPU -> Disk BW (GB/s)"] = round(bw_gb_s, 2)
            results["GPU -> Disk IOPS"] = int(iops)
    except Exception as e:  # broad catch to continue other tests
        results["GPU -> Disk BW (GB/s)"] = f"Failed ({e.__class__.__name__})"
        results["GPU -> Disk IOPS"] = f"Failed ({e.__class__.__name__})"

    # Clear tensor before read
    tensor.zero_()
    torch.cuda.synchronize()

    # --- Disk -> GPU (read) ---
    try:
        with CuFile(file_path, "r", use_direct_io=USE_DIRECT_IO) as f:
            torch.cuda.synchronize()
            start = time.perf_counter()
            f.read(dev_ptr, FILE_SIZE, file_offset=0, dev_offset=0)
            torch.cuda.synchronize()
            end = time.perf_counter()
            elapsed = end - start
            bw_gb_s = FILE_SIZE / elapsed / 1e9  # GB/s
            iops = (bw_gb_s * 1e9) / BLOCK_SIZE
            results["Disk -> GPU BW (GB/s)"] = round(bw_gb_s, 2)
            results["Disk -> GPU IOPS"] = int(iops)
    except Exception as e:
        results["Disk -> GPU BW (GB/s)"] = f"Failed ({e.__class__.__name__})"
        results["Disk -> GPU IOPS"] = f"Failed ({e.__class__.__name__})"

    # Cleanup
    try:
        os.remove(file_path)
    except OSError:
        pass

    return results

def get_disk_info() -> dict:
    """Gather disk performance information for both CPU and GPU paths."""
    mountpoint = get_nvme_mountpoint()

    result: dict[str, object] = {"NVMe Detected": mountpoint != "/tmp"}

    # --- CPU <-> Disk benchmarks via fio ---
    bench_dir = os.path.join(mountpoint, "fio-multifile")
    Path(bench_dir).mkdir(parents=True, exist_ok=True)

    result.update(run_fio_test(bench_dir, "read"))   # Disk -> CPU
    result.update(run_fio_test(bench_dir, "write"))  # CPU -> Disk

    # Cleanup benchmark files generated by fio
    try:
        for f in Path(bench_dir).iterdir():
            f.unlink(missing_ok=True)  # type: ignore[arg-type]
        Path(bench_dir).rmdir()
    except OSError:
        pass

    # --- GPU <-> Disk benchmarks via CuFile ---
    result.update(run_gpu_disk_benchmark(mountpoint))

    return result


# 4. NIC

def get_nic_info():
    pass

# --- Main ---

if __name__ == "__main__":
    results = {}
    results["GPU"] = get_gpu_info()
    results["CPU"] = get_cpu_info()
    results["Disk"] = get_disk_info()
    results["NIC"] = get_nic_info()
    print(json.dumps(results, indent=2))
