# QuickStart

Should be on some Linux Machine with CUDA installed

Dependencies:

```bash
pip install torch
sudo apt install -y nvidia-fs-dkms nvidia-fs-tools
sudo apt install -y fio nvidia-gds
/opt/nvidia/gds/tools/gdscheck.py
```

Run: 
```bash
# result will be printed to stdout
python diagnostics.py
```

Example Output:
```text
[diagnostics] Starting system diagnostics
[diagnostics] Collecting GPU info…
[diagnostics] Collecting CPU info…
[diagnostics] Running disk benchmarks (this may take a minute)…
[diagnostics] Collecting NIC / RDMA info…
[diagnostics] Diagnostics complete
{
  "GPU": {
    "GPU Type": "H100",
    "GPU VRAM": "81559 MiB",
    "VRAM Type": "HBM3",
    "GPU Count": 8,
    "Has NVLink": true,
    "NVLink Bonds": {
      "GPU0": [
        [
          "GPU1",
          18
        ],
        [
          "GPU2",
          18
        ],
        [
          "GPU3",
          18
        ],
        [
          "GPU4",
          18
        ],
        [
          "GPU5",
          18
        ],
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU1": [
        [
          "GPU2",
          18
        ],
        [
          "GPU3",
          18
        ],
        [
          "GPU4",
          18
        ],
        [
          "GPU5",
          18
        ],
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU2": [
        [
          "GPU3",
          18
        ],
        [
          "GPU4",
          18
        ],
        [
          "GPU5",
          18
        ],
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU3": [
        [
          "GPU4",
          18
        ],
        [
          "GPU5",
          18
        ],
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU4": [
        [
          "GPU5",
          18
        ],
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU5": [
        [
          "GPU6",
          18
        ],
        [
          "GPU7",
          18
        ]
      ],
      "GPU6": [
        [
          "GPU7",
          18
        ]
      ]
    }
  },
  "CPU": {
    "Chip Architecture": "x86_64",
    "CPU Model": "INTEL(R) XEON(R) PLATINUM 8558",
    "CPU Core Count": 96,
    "CPU Thread Count": 192,
    "Operating System": "Ubuntu 22.04.5 LTS",
    "RAM Size": "2.0Ti",
    "PCIe Gen": 5,
    "Link Width": 16,
    "Estimated BW (GB/s)": 64.0
  },
  "Disk": {
    "NVMe Detected": true,
    "Disk -> CPU BW (GB/s)": 5.65,
    "Disk -> CPU IOPS": 180,
    "CPU -> Disk BW (GB/s)": 0.85,
    "CPU -> Disk IOPS": 27,
    "GPU -> Disk BW (GB/s)": 0.75,
    "GPU -> Disk IOPS": 179,
    "Disk -> GPU BW (GB/s)": 5.33,
    "Disk -> GPU IOPS": 1270
  },
  "NIC": {
    "RDMA NICs": 11,
    "IB Device Count": 0,
    "Device Transport Types": {
      "mlx5_0": "InfiniBand",
      "mlx5_1": "InfiniBand",
      "mlx5_11": "InfiniBand",
      "mlx5_2": "InfiniBand",
      "mlx5_3": "InfiniBand",
      "mlx5_4": "InfiniBand",
      "mlx5_5": "InfiniBand",
      "mlx5_6": "InfiniBand",
      "mlx5_7": "InfiniBand",
      "mlx5_8": "InfiniBand",
      "mlx5_bond_0": "InfiniBand"
    },
    "Total NICs": 14,
    "Mellanox Device Count": 12,
    "Mellanox PCI Entries": [
      "19:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "29:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "3b:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "53:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "5c:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "85:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "8a:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "92:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "9f:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
      "a2:00.0 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]",
      "a2:00.1 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]",
      "e3:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]"
    ],
    "Mellanox PCI Details": {
      "19:00.0": {
        "Description": "19:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "29:00.0": {
        "Description": "29:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "3b:00.0": {
        "Description": "3b:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "53:00.0": {
        "Description": "53:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "5c:00.0": {
        "Description": "5c:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "85:00.0": {
        "Description": "85:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "8a:00.0": {
        "Description": "8a:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "92:00.0": {
        "Description": "92:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "9f:00.0": {
        "Description": "9f:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      },
      "a2:00.0": {
        "Description": "a2:00.0 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]",
        "BW (GB/s)": 32.0
      },
      "a2:00.1": {
        "Description": "a2:00.1 Ethernet controller: Mellanox Technologies MT2892 Family [ConnectX-6 Dx]",
        "BW (GB/s)": 32.0
      },
      "e3:00.0": {
        "Description": "e3:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]",
        "BW (GB/s)": 64.0
      }
    },
    "RDMA Drivers Loaded": [
      "rdma_ucm",
      "rdma_cm",
      "iw_cm",
      "ib_cm",
      "mlx5_ib",
      "ib_uverbs",
      "ib_core",
      "mlx5_core",
      "pci_hyperv_intf",
      "mlxdevm",
      "tls",
      "mlxfw",
      "mlx_compat",
      "psample"
    ],
    "rdma-core Installed": true,
    "MLNX_OFED Version": "24.10-2.1.8",
    "NIC PCIe BW (GB/s)": {
      "19:00.0": 64.0,
      "29:00.0": 64.0,
      "3b:00.0": 64.0,
      "53:00.0": 64.0,
      "56:00.0": 4.0,
      "56:00.1": 4.0,
      "5c:00.0": 64.0,
      "85:00.0": 64.0,
      "8a:00.0": 64.0,
      "92:00.0": 64.0,
      "9f:00.0": 64.0,
      "a2:00.0": 32.0,
      "a2:00.1": 32.0,
      "e3:00.0": 64.0
    }
  }
}
[diagnostics] Generating LMCache recommendations…


LMCache Configuration Report
------------------------------
Recommended LMCACHE_MAX_LOCAL_CPU_SIZE total (split across workers): 1638.4 GB (~80% of CPU RAM)
Recommended LMCACHE_MAX_LOCAL_DISK_SIZE total (split across workers): 256.8 GB (~80% of available disk)
Disk Configuration:
  • Disk → CPU BW: 5.65 GB/s
  • CPU → Disk BW: 0.85 GB/s
GDS (GPU Direct Storage):
  • GDS enabled: True
  • Disk → GPU BW: 5.33 GB/s
  • GPU → Disk BW: 0.75 GB/s
Network: Peak NIC PCIe BW: 64.0 GB/s (High)
Intra-node Prefill Disaggregation (NVLink): True (connected GPUs: 8)
Cross-node Prefill Disaggregation (RDMA/Infiniband): True
--------------------------------
```

# Metrics

1. GPU
- GPU Type
- GPU VRAM
- VRAM Type
- GPU Count
- Has NVLink
- NVLink Bond Map

Commands:
```bash
nvidia-smi --query-gpu=name --format=csv,noheader
# Connection matrix
nvidia-smi topo -m
```

2. CPU
- Chip Architecture
- Model Name
- Core Count
- Operating System
- RAM size
- CPU <--> GPU memory speed (by checking PCIE generation and width)

Commands: 
```bash
lscpu
cat /etc/os-release
free -h
nvidia-smi -q
```

3. Disk
- NVMe SSDs
- Disk <-> CPU Memory IO speed
- Disk <-> GPU Memory IO speed (via GDS)

Commands: 
```bash
lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme

rm /tmp/fio-multifile
mkdir /tmp/fio-multifile
# 0.313 GB file block reads (256 token chunks for Llama 8B)
# Disk -> CPU
fio --name=cpu-readtest \
    --directory=/tmp/fio-multifile \
    --size=1G \
    --bs=32M \
    --rw=read \
    --ioengine=libaio \
    --direct=1 \
    --numjobs=4 \
    --iodepth=32 \
    --group_reporting

# CPU -> Disk
fio --name=cpu-writetest \
    --directory=/tmp/fio-multifile \
    --size=1G \
    --bs=32M \
    --rw=write \
    --ioengine=libaio \
    --direct=1 \
    --numjobs=4 \
    --iodepth=32 \
    --group_reporting

# GPU <-> Disk
sudo mkdir -p /mnt/nvme0n1p1
sudo mount /dev/nvme0n1p1 /mnt/nvme0n1p1
sudo chown $USER:$USER /mnt/nvme0n1p1
```

4. NIC
- RDMA devices present?                    # /sys/class/infiniband
- InfiniBand transport active?            # ibv_devinfo | grep transport
- Mellanox (MLNX) NICs present?           # lspci | grep -i mell
- NIC PCIe bandwidth (speed × width)?     # lspci -vv | grep -A1 LnkCap
- RDMA drivers loaded (kernel modules)?   # lsmod | grep 'ib_core|mlx5_core|...'
- rdma-core (user-space tools) installed? # dpkg -l | grep rdma-core
- MLNX_OFED installed?                    # modinfo mlx5_core | grep version

Commands:
```bash
# Number of RDMA devices
echo -n "RDMA devices: "
ls /sys/class/infiniband 2>/dev/null | wc -l

# Number of IB devices
echo -n "InfiniBand (IB) devices: "
ib_count=0
for dev in $(ls /sys/class/infiniband 2>/dev/null); do
    if ibv_devinfo -d "$dev" | grep -q "transport: IB"; then
        ((ib_count++))
    fi
done
echo "$ib_count"

# Print transport type for each RDMA device
echo "Device transport types:"
for dev in $(ls /sys/class/infiniband 2>/dev/null); do
    echo -n "$dev: "
    ibv_devinfo -d "$dev" | grep "transport"
done

# Number of Mellanox devices
echo -n "Mellanox (MLNX) PCI devices: "
lspci | grep -i mell | wc -l

# Optional: print full Mellanox PCI lines
echo "Mellanox PCI entries:"
lspci | grep -i mell

# Check for drivers:
lsmod | grep -E 'ib_core|mlx5_core|mlx5_ib|ib_uverbs|rdma_ucm|rdma_cm'

# NIC Bandwidth: PCIe Link speed x width
sudo lspci -s 19:00.0 -vv
```