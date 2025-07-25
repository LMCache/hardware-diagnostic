# Overview

Does your machine have the necessary HW/SW dependencies to enable certain features of LMCache (CPU offload, Disk Offload Latency, Remote Latency, GDS, Intra and Inter Node PD)? 

# QuickStart

Should be on some Linux Machine with CUDA installed

Dependencies:

```bash
pip install torch numpy
sudo apt install -y util-linux
sudo apt install -y nvidia-fs-dkms 
sudo apt install -y fio 

# mainly for GDS, skip if you don't care about these metrics
sudo mkdir -p /usr/share/keyrings
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub \
  | gpg --dearmor | sudo tee /usr/share/keyrings/cuda-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/cuda-archive-keyring.gpg] \
https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" \
| sudo tee /etc/apt/sources.list.d/cuda.list > /dev/null

sudo apt update
sudo apt install -y libcufile-12-8 libcufile-dev-12-8 gds-tools-12-8
sudo ln -s /usr/local/cuda-12.8/targets/x86_64-linux/lib/libcufile.so.1.13.1 \
  /usr/local/cuda-12.8/targets/x86_64-linux/lib/libcufile.so || true
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.8/targets/x86_64-linux/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

Run: 
```bash
python diagnostics.py
```

Examples of outputs can be found in `results.txt`

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