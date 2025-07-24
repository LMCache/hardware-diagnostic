import subprocess
import re
import json
import os
import sys
from pathlib import Path
import ctypes
import time

def safe_run(cmd: str) -> str | None:
    """Run a shell command and return its stdout, or None if it fails.
    All stderr output is suppressed to keep logs clean."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Record the failure for later diagnostics
        _log_command_error(cmd, str(e))
        return None


# ---------------- Error logging & progress helpers -----------------

# Accumulates all command failures so they can be surfaced at the end
ERRORS: list[str] = []

# Quick suggestions to help the user resolve missing tools
_SUGGESTIONS: dict[str, str] = {
    "nvidia-smi": "Install NVIDIA drivers / CUDA toolkit to get nvidia-smi.",
    "lspci": "Install pciutils (e.g. `sudo apt install pciutils`).",
    "lsblk": "Install util-linux (e.g. `sudo apt install util-linux`).",
    "fio": "Install fio benchmark tool (e.g. `sudo apt install fio`).",
    "ibv_devinfo": "Install rdma-core (e.g. `sudo apt install rdma-core`).",
    "modinfo": "Install kmod (e.g. `sudo apt install kmod`).",
    "lsmod": "Install kmod (e.g. `sudo apt install kmod`).",
    "ibstat": "Install rdma-core for InfiniBand diagnostics.",
    "cufile": "Install NVIDIA GDS libraries (`nvidia-fs-dkms` and `nvidia-fs-tools`).",
}


def _log_command_error(cmd: str, err: str) -> None:
    exe = cmd.split()[0]
    suggestion = _SUGGESTIONS.get(exe)
    msg = f"Command failed: '{cmd}'. Error: {err}"
    if suggestion:
        msg += f". Suggestion: {suggestion}"
    ERRORS.append(msg)


def progress(msg: str) -> None:
    """Print a progress message immediately (stderr) so the user sees activity."""
    print(f"[diagnostics] {msg}", file=sys.stderr, flush=True)

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

# Map PCIe line rate (GT/s) to generation index used in BANDWIDTH_PER_LANE_GB
GT_TO_GEN = {2: 1, 5: 2, 8: 3, 16: 4, 32: 5, 64: 6}

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

    if bw_match:
        bw_mib = int(bw_match.group(1))
        bw_gb = round(bw_mib / 1024, 2)  # Convert to GB/s (base-2 GiB/s approx)
    else:
        bw_gb = "Unknown"

    return {
        f"{prefix} BW (GB/s)": bw_gb,
        f"{prefix} IOPS": int(iops_match.group(1)) if iops_match else "Unknown"
    }


# ---------------- NIC helpers -----------------


def parse_nic_bandwidth() -> dict:
    """Return NIC PCIe bandwidth keyed by PCI address as {addr: GB/s}."""

    output = safe_run("lspci | grep -E 'Ethernet controller|Infiniband controller|Network controller'")
    if not output:
        return {"NIC PCIe BW (GB/s)": "Unavailable"}

    bandwidths: dict[str, float] = {}
    for line in output.splitlines():
        pci_addr = line.split()[0]
        detail = safe_run(f"sudo lspci -s {pci_addr} -vv")
        if not detail:
            continue

        # Prefer LnkSta, fall back to LnkCap
        lnk_line = next((l for l in detail.splitlines() if "LnkSta:" in l), "")
        if not lnk_line:
            lnk_line = next((l for l in detail.splitlines() if "LnkCap:" in l), "")
        if not lnk_line:
            continue

        speed_match = re.search(r"Speed\s+([0-9.]+)GT/s", lnk_line)
        width_match = re.search(r"Width\s+x([0-9]+)", lnk_line)
        if not (speed_match and width_match):
            continue

        gt = float(speed_match.group(1))
        width = int(width_match.group(1))
        gen_key = int(round(gt))
        gen = GT_TO_GEN.get(gen_key)

        if gen and gen in BANDWIDTH_PER_LANE_GB:
            bw = BANDWIDTH_PER_LANE_GB[gen] * width
        else:
            bw = gt * 0.985 * width * 0.125  # rough fallback

        bandwidths[pci_addr] = round(bw, 2)

    return {"NIC PCIe BW (GB/s)": bandwidths or "Unavailable"}


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
    """Collect NIC/RDMA related information following section 4 of the README.

    The function tries to stay resilient on systems that may not have RDMA / Mellanox
    hardware or the related user-space tools installed. Any missing information is
    marked as "Unknown" rather than raising.
    """

    info: dict[str, object] = {}

    # --- RDMA & IB devices --------------------------------------------------
    rdma_devs_output = safe_run("ls /sys/class/infiniband")
    rdma_devices = rdma_devs_output.splitlines() if rdma_devs_output else []
    info["RDMA NICs"] = len(rdma_devices)

    ib_device_count = 0
    transport_types: dict[str, str] = {}
    for dev in rdma_devices:
        devinfo_out = safe_run(f"ibv_devinfo -d {dev} | grep transport")
        if devinfo_out:
            # Example line: "\ttransport:          InfiniBand (0)"
            transport_match = re.search(r"transport:\s*([A-Za-z]+)", devinfo_out)
            if transport_match:
                transport_types[dev] = transport_match.group(1)
                if transport_match.group(1).lower().startswith("ib"):
                    ib_device_count += 1
        else:
            # Fallback if ibv_devinfo is absent – mark as unknown.
            transport_types[dev] = "Unknown"

    info["IB Device Count"] = ib_device_count
    if transport_types:
        info["Device Transport Types"] = transport_types

    # --- Total NICs via lspci ----------------------------------------------
    nic_pci_out = safe_run("lspci | grep -E 'Ethernet controller|Infiniband controller|Network controller'")
    nic_lines = nic_pci_out.splitlines() if nic_pci_out else []
    info["Total NICs"] = len(nic_lines)

    # --- Mellanox devices via PCI-IDs --------------------------------------
    mlx_lines = [line for line in nic_lines if re.search(r"mell", line, flags=re.IGNORECASE)]
    info["Mellanox Device Count"] = len(mlx_lines)

    # --- NIC PCIe bandwidth (run once to reuse) ----------------------------
    bandwidth_result = parse_nic_bandwidth()
    nic_bw_map = bandwidth_result.get("NIC PCIe BW (GB/s)") if isinstance(bandwidth_result, dict) else {}

    if mlx_lines:
        info["Mellanox PCI Entries"] = mlx_lines

        # Coupled details: map PCI addr → description & BW
        mell_details: dict[str, dict[str, object]] = {}
        for line in mlx_lines:
            pci_addr = line.split()[0]
            mell_details[pci_addr] = {
                "Description": line,
                "BW (GB/s)": nic_bw_map.get(pci_addr, "Unknown") if isinstance(nic_bw_map, dict) else "Unknown",
            }
        info["Mellanox PCI Details"] = mell_details

    # --- Loaded RDMA driver modules ----------------------------------------
    driver_out = safe_run("lsmod | grep -E 'ib_core|mlx5_core|mlx5_ib|ib_uverbs|rdma_ucm|rdma_cm'")
    drivers: list[str] = []
    if driver_out:
        for line in driver_out.splitlines():
            module_name = line.split()[0]
            drivers.append(module_name)
    info["RDMA Drivers Loaded"] = drivers or "None"

    # --- rdma-core user-space tools installed? -----------------------------
    rdma_core_installed = False
    if safe_run("dpkg -l | grep rdma-core"):
        rdma_core_installed = True
    elif safe_run("rpm -qa | grep rdma-core"):
        rdma_core_installed = True
    info["rdma-core Installed"] = rdma_core_installed

    # --- MLNX_OFED version --------------------------------------------------
    ofed_version_line = safe_run("modinfo mlx5_core | grep ^version")
    info["MLNX_OFED Version"] = ofed_version_line.split()[-1] if ofed_version_line else "Unknown"

    # --- PCIe bandwidth -----------------------------------------------------
    info.update(bandwidth_result)

    return info


# --- Main ---

if __name__ == "__main__":
    progress("Starting system diagnostics")

    results: dict[str, object] = {}

    progress("Collecting GPU info…")
    results["GPU"] = get_gpu_info()

    progress("Collecting CPU info…")
    results["CPU"] = get_cpu_info()

    progress("Running disk benchmarks (this may take a minute)…")
    results["Disk"] = get_disk_info()

    progress("Collecting NIC / RDMA info…")
    results["NIC"] = get_nic_info()

    # Append any captured errors
    if ERRORS:
        results["Errors"] = ERRORS

    progress("Diagnostics complete")

    print(json.dumps(results, indent=2))

    # ---------------- LMCache report -----------------
    def _size_str_to_gb(size_str: str) -> float | None:
        """Convert strings like '128G', '62Gi', '512M' to GB (binary GiB)."""
        match = re.match(r"([0-9.]+)\s*([KMGTP])", size_str, flags=re.IGNORECASE)
        if not match:
            return None
        val = float(match.group(1))
        unit = match.group(2).upper()
        factor = {"K": 1/1024/1024, "M": 1/1024, "G": 1, "T": 1024, "P": 1024*1024}.get(unit)
        if factor is None:
            return None
        return round(val * factor, 2)

    def _available_disk_gb(path: str) -> float | None:
        df_out = safe_run(f"df -BG --output=avail {path} | tail -1")
        if not df_out:
            return None
        try:
            gb = int(df_out.strip()[:-1])  # strip trailing 'G'
            return float(gb)
        except ValueError:
            return None

    progress("Generating LMCache recommendations…")

    cpu_ram_str = results.get("CPU", {}).get("RAM Size", "")  # e.g. '125G'
    total_ram_gb = _size_str_to_gb(cpu_ram_str) or 0
    rec_cpu = round(total_ram_gb * 0.8, 2)

    # Disk availability
    mountpoint = get_nvme_mountpoint()
    avail_disk_gb = _available_disk_gb(mountpoint) or 0
    rec_disk = round(avail_disk_gb * 0.8, 2)

    # GDS enabled? (CuFile import + GPU available)
    try:
        import torch  # type: ignore
        import cufile  # type: ignore
        gds_enabled = torch.cuda.is_available()
    except Exception:
        gds_enabled = False

    nvlink = results.get("GPU", {}).get("Has NVLink", False)
    rdma_present = results.get("NIC", {}).get("RDMA NICs", 0) > 0

    # Network BW estimate – use max NIC PCIe BW as basic proxy
    nic_bw_map = results.get("NIC", {}).get("NIC PCIe BW (GB/s)", {})
    if isinstance(nic_bw_map, dict) and nic_bw_map:
        peak_nic_bw = max(nic_bw_map.values())
    else:
        peak_nic_bw = None

    if isinstance(peak_nic_bw, (int, float)):
        if peak_nic_bw >= 50:
            nic_class = "High"
        elif peak_nic_bw >= 32:
            nic_class = "Medium"
        else:
            nic_class = "Low (CacheGen recommended)"
    else:
        nic_class = "Unknown"

    # Disk BW subpoints
    disk_section = results.get("Disk", {})
    disk_read_bw = disk_section.get("Disk -> CPU BW (GB/s)")
    disk_write_bw = disk_section.get("CPU -> Disk BW (GB/s)")

    # GDS BW subpoints
    gds_read_bw = disk_section.get("Disk -> GPU BW (GB/s)")
    gds_write_bw = disk_section.get("GPU -> Disk BW (GB/s)")

    # NVLink node count
    nv_bonds = results.get("GPU", {}).get("NVLink Bonds") or {}
    connected_gpus = set()
    for src, pairs in nv_bonds.items():
        connected_gpus.add(src)
        for dst, _ in pairs:
            connected_gpus.add(dst)
    nvlink_nodes = len(connected_gpus)

    print("\n\nLMCache Configuration Report")
    print("------------------------------")
    print(f"Recommended LMCACHE_MAX_LOCAL_CPU_SIZE total (split across workers): {rec_cpu} GB (~80% of CPU RAM)")
    print(f"Recommended LMCACHE_MAX_LOCAL_DISK_SIZE total (split across workers): {rec_disk} GB (~80% of available disk)")

    # Disk configuration details
    print("Disk Configuration:")
    print(f"  • Disk → CPU BW: {disk_read_bw} GB/s")
    print(f"  • CPU → Disk BW: {disk_write_bw} GB/s")

    # GDS details
    print("GDS (GPU Direct Storage):")
    print(f"  • GDS enabled: {gds_enabled}")
    print(f"  • Disk → GPU BW: {gds_read_bw} GB/s")
    print(f"  • GPU → Disk BW: {gds_write_bw} GB/s")

    # Network & PD
    nic_bw_display = peak_nic_bw if peak_nic_bw is not None else "Unknown"
    print(f"Network: Peak NIC PCIe BW: {nic_bw_display} GB/s ({nic_class})")
    print(f"Intra-node Prefill Disaggregation (NVLink): {nvlink} (connected GPUs: {nvlink_nodes})")
    print(f"Cross-node Prefill Disaggregation (RDMA/Infiniband): {rdma_present}")
    print("--------------------------------\n\n\n")