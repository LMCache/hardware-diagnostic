# Example Outputs on various machines

1. 8x H100 GMI node:
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
    "Disk -> CPU BW (GB/s)": 5.27,
    "Disk -> CPU IOPS": 168,
    "CPU -> Disk BW (GB/s)": 0.86,
    "CPU -> Disk IOPS": 27,
    "GPU -> Disk BW (GB/s)": 0.77,
    "GPU -> Disk IOPS": 183,
    "Disk -> GPU BW (GB/s)": 5.38,
    "Disk -> GPU IOPS": 1281
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
Recommended LMCACHE_MAX_LOCAL_DISK_SIZE total (split across workers): 219.2 GB (~80% of available disk)
Disk Configuration:
  • Disk → CPU BW: 5.27 GB/s
  • CPU → Disk BW: 0.86 GB/s
GDS (GPU Direct Storage):
  • GDS enabled: True
  • Disk → GPU BW: 5.38 GB/s
  • GPU → Disk BW: 0.77 GB/s
Network: Peak NIC PCIe BW: 64.0 GB/s (High)
Intra-node Prefill Disaggregation Possible (via NVLink): True (connected GPUs: 8)
Cross-node Prefill Disaggregation Possible (via RDMA/Infiniband): True
--------------------------------
```

2. 1x H100 (80 GB SXM5) 26 vCPUs, 225 GiB RAM, 2.8 TiB SSD
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
    "GPU Count": 1,
    "Has NVLink": true,
    "NVLink Bonds": null
  },
  "CPU": {
    "Chip Architecture": "x86_64",
    "CPU Model": "Intel(R) Xeon(R) Platinum 8480+",
    "CPU Core Count": 13,
    "CPU Thread Count": 26,
    "Operating System": "Ubuntu 22.04.5 LTS",
    "RAM Size": "221Gi",
    "PCIe Gen": 5,
    "Link Width": 16,
    "Estimated BW (GB/s)": 64.0
  },
  "Disk": {
    "NVMe Detected": false,
    "Disk -> CPU BW (GB/s)": "Unknown",
    "Disk -> CPU IOPS": 350,
    "CPU -> Disk BW (GB/s)": 6.91,
    "CPU -> Disk IOPS": 221,
    "GPU -> Disk BW (GB/s)": "cufile or torch unavailable",
    "GPU -> Disk IOPS": "cufile or torch unavailable",
    "Disk -> GPU BW (GB/s)": "cufile or torch unavailable",
    "Disk -> GPU IOPS": "cufile or torch unavailable"
  },
  "NIC": {
    "RDMA NICs": 1,
    "IB Device Count": 0,
    "Device Transport Types": {
      "mlx5_0": "InfiniBand"
    },
    "Total NICs": 1,
    "Mellanox Device Count": 1,
    "Mellanox PCI Entries": [
      "05:00.0 Ethernet controller: Mellanox Technologies ConnectX Family mlx5Gen Virtual Function"
    ],
    "Mellanox PCI Details": {
      "05:00.0": {
        "Description": "05:00.0 Ethernet controller: Mellanox Technologies ConnectX Family mlx5Gen Virtual Function",
        "BW (GB/s)": "Unknown"
      }
    },
    "RDMA Drivers Loaded": [
      "rdma_ucm",
      "rdma_cm",
      "iw_cm",
      "ib_cm",
      "mlx5_ib",
      "macsec",
      "ib_uverbs",
      "ib_core",
      "mlx5_core",
      "mlxfw",
      "psample",
      "mlxdevm",
      "tls",
      "mlx_compat",
      "pci_hyperv_intf"
    ],
    "rdma-core Installed": true,
    "MLNX_OFED Version": "24.10-2.1.8",
    "NIC PCIe BW (GB/s)": "Unavailable"
  },
  "Errors": [
    "Command failed: 'lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme'. Error: Command 'lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme' returned non-zero exit status 1.. Suggestion: NVMe is disabled (This is not a real error, just a warning)."
  ]
}
[diagnostics] Generating LMCache recommendations…


LMCache Configuration Report
------------------------------
Recommended LMCACHE_MAX_LOCAL_CPU_SIZE total (split across workers): 176.8 GB (~80% of CPU RAM)
Recommended LMCACHE_MAX_LOCAL_DISK_SIZE total (split across workers): 2160.0 GB (~80% of available disk)
Disk Configuration:
  • Disk → CPU BW: Unknown GB/s
  • CPU → Disk BW: 6.91 GB/s
GDS (GPU Direct Storage):
  • GDS enabled: False
  • Disk → GPU BW: cufile or torch unavailable GB/s
  • GPU → Disk BW: cufile or torch unavailable GB/s
Network: Peak NIC PCIe BW: Unknown GB/s (Unknown)
Intra-node Prefill Disaggregation Possible (via NVLink): True (connected GPUs: 0)
Cross-node Prefill Disaggregation Possible (via RDMA/Infiniband): True
--------------------------------
```


3. 1x H100 (80 GB PCIe) 26 vCPUs, 200 GiB RAM, 1 TiB SSD

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
    "VRAM Type": "Unknown",
    "GPU Count": 1,
    "Has NVLink": true,
    "NVLink Bonds": null
  },
  "CPU": {
    "Chip Architecture": "x86_64",
    "CPU Model": "Intel(R) Xeon(R) Platinum 8480+",
    "CPU Core Count": 26,
    "CPU Thread Count": 26,
    "Operating System": "Ubuntu 22.04.5 LTS",
    "RAM Size": "221Gi",
    "PCIe Gen": 5,
    "Link Width": 16,
    "Estimated BW (GB/s)": 64.0
  },
  "Disk": {
    "NVMe Detected": false,
    "Disk -> CPU BW (GB/s)": 8.75,
    "Disk -> CPU IOPS": 280,
    "CPU -> Disk BW (GB/s)": 2.9,
    "CPU -> Disk IOPS": 92,
    "GPU -> Disk BW (GB/s)": "cufile or torch unavailable",
    "GPU -> Disk IOPS": "cufile or torch unavailable",
    "Disk -> GPU BW (GB/s)": "cufile or torch unavailable",
    "Disk -> GPU IOPS": "cufile or torch unavailable"
  },
  "NIC": {
    "RDMA NICs": 1,
    "IB Device Count": 0,
    "Device Transport Types": {
      "mlx5_0": "InfiniBand"
    },
    "Total NICs": 1,
    "Mellanox Device Count": 1,
    "Mellanox PCI Entries": [
      "05:00.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function]"
    ],
    "Mellanox PCI Details": {
      "05:00.0": {
        "Description": "05:00.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function]",
        "BW (GB/s)": "Unknown"
      }
    },
    "RDMA Drivers Loaded": [
      "rdma_ucm",
      "rdma_cm",
      "iw_cm",
      "ib_cm",
      "mlx5_ib",
      "macsec",
      "ib_uverbs",
      "ib_core",
      "mlx5_core",
      "mlxfw",
      "psample",
      "mlxdevm",
      "tls",
      "mlx_compat",
      "pci_hyperv_intf"
    ],
    "rdma-core Installed": true,
    "MLNX_OFED Version": "24.10-2.1.8",
    "NIC PCIe BW (GB/s)": "Unavailable"
  },
  "Errors": [
    "Command failed: 'lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme'. Error: Command 'lsblk -o NAME,HCTL,SIZE,MOUNTPOINT,MODEL | grep nvme' returned non-zero exit status 1.. Suggestion: NVMe is disabled (This is not a real error, just a warning)."
  ]
}
[diagnostics] Generating LMCache recommendations…


LMCache Configuration Report
------------------------------
Recommended LMCACHE_MAX_LOCAL_CPU_SIZE total (split across workers): 176.8 GB (~80% of CPU RAM)
Recommended LMCACHE_MAX_LOCAL_DISK_SIZE total (split across workers): 765.6 GB (~80% of available disk)
Disk Configuration:
  • Disk → CPU BW: 8.75 GB/s
  • CPU → Disk BW: 2.9 GB/s
GDS (GPU Direct Storage):
  • GDS enabled: False
  • Disk → GPU BW: cufile or torch unavailable GB/s
  • GPU → Disk BW: cufile or torch unavailable GB/s
Network: Peak NIC PCIe BW: Unknown GB/s (Unknown)
Intra-node Prefill Disaggregation Possible (via NVLink): True (connected GPUs: 0)
Cross-node Prefill Disaggregation Possible (via RDMA/Infiniband): True
--------------------------------
```