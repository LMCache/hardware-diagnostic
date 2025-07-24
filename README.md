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
python diagnostics.py
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
