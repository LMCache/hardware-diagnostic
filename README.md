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
# result will be printed to stdout as well as diagnostics.html
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
19:00.0 Infiniband controller: Mellanox Technologies MT2910 Family [ConnectX-7]
        Subsystem: Mellanox Technologies MT2910 Family [ConnectX-7]
        Physical Slot: 2-1
        Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr+ Stepping- SERR+ FastB2B- DisINTx+
        Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
        Latency: 0, Cache Line Size: 32 bytes
        Interrupt: pin A routed to IRQ 17
        NUMA node: 0
        Region 0: Memory at 5e044000000 (64-bit, prefetchable) [size=32M]
        Expansion ROM at a3e00000 [disabled] [size=1M]
        Capabilities: [60] Express (v2) Endpoint, MSI 00
                DevCap: MaxPayload 512 bytes, PhantFunc 0, Latency L0s unlimited, L1 unlimited
                        ExtTag+ AttnBtn- AttnInd- PwrInd- RBE+ FLReset+ SlotPowerLimit 75.000W
                DevCtl: CorrErr- NonFatalErr- FatalErr+ UnsupReq-
                        RlxdOrd+ ExtTag+ PhantFunc- AuxPwr- NoSnoop+ FLReset-
                        MaxPayload 256 bytes, MaxReadReq 512 bytes
                DevSta: CorrErr- NonFatalErr- FatalErr- UnsupReq- AuxPwr- TransPend-
                LnkCap: Port #0, Speed 32GT/s, Width x16, ASPM not supported
                        ClockPM- Surprise- LLActRep- BwNot- ASPMOptComp+
                LnkCtl: ASPM Disabled; RCB 64 bytes, Disabled- CommClk-
                        ExtSynch- ClockPM- AutWidDis- BWInt- AutBWInt-
                LnkSta: Speed 32GT/s (ok), Width x16 (ok)
                        TrErr- Train- SlotClk+ DLActive- BWMgmt- ABWMgmt-
                DevCap2: Completion Timeout: Range ABC, TimeoutDis+ NROPrPrP- LTR-
                         10BitTagComp+ 10BitTagReq+ OBFF Not Supported, ExtFmt- EETLPPrefix-
                         EmergencyPowerReduction Not Supported, EmergencyPowerReductionInit-
                         FRS- TPHComp- ExtTPHComp-
                         AtomicOpsCap: 32bit+ 64bit+ 128bitCAS+
                DevCtl2: Completion Timeout: 260ms to 900ms, TimeoutDis- LTR- OBFF Disabled,
                         AtomicOpsCtl: ReqEn+
                LnkCap2: Supported Link Speeds: 2.5-32GT/s, Crosslink- Retimer+ 2Retimers+ DRS-
                LnkCtl2: Target Link Speed: 32GT/s, EnterCompliance- SpeedDis-
                         Transmit Margin: Normal Operating Range, EnterModifiedCompliance- ComplianceSOS-
                         Compliance De-emphasis: -6dB
                LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+ EqualizationPhase1+
                         EqualizationPhase2+ EqualizationPhase3+ LinkEqualizationRequest-
                         Retimer- 2Retimers- CrosslinkRes: unsupported
        Capabilities: [48] Vital Product Data
                Product Name: NVIDIA ConnectX-7 HHHL Adapter card, 400GbE / NDR IB (default mode), Single-port OSFP, PCIe 5.0 x16, Crypto Disabled, Secure Boot Enabled                                             
                Read-only fields:
                        [PN] Part number: MCX75310AAS-NEAT         
                        [EC] Engineering changes: AA
                        [V2] Vendor specific: MCX75310AAS-NEAT         
                        [SN] Serial number: MT2347J0100T   
                        [V3] Vendor specific: dc99c18c2e8bee11800058a2e10d4bce
                        [VA] Vendor specific: MLX:MN=MLNX:CSKU=V2:UUID=V3:PCI=V0:MODL=CX75310AA      
                        [V0] Vendor specific: PCIeGen5 x16 
                        [VU] Vendor specific: MT2347J0100TMLNXS0D0F0 
                        [RV] Reserved: checksum good, 1 byte(s) reserved
                End
        Capabilities: [9c] MSI-X: Enable+ Count=64 Masked-
                Vector table: BAR=0 offset=00002000
                PBA: BAR=0 offset=00003000
        Capabilities: [c0] Vendor Specific Information: Len=18 <?>
        Capabilities: [40] Power Management version 3
                Flags: PMEClk- DSI- D1- D2- AuxCurrent=375mA PME(D0-,D1-,D2-,D3hot-,D3cold+)
                Status: D0 NoSoftRst+ PME-Enable- DSel=0 DScale=0 PME-
        Capabilities: [100 v1] Advanced Error Reporting
                UESta:  DLP- SDES- TLP- FCP- CmpltTO- CmpltAbrt- UnxCmplt- RxOF- MalfTLP- ECRC- UnsupReq- ACSViol-
                UEMsk:  DLP- SDES- TLP- FCP- CmpltTO- CmpltAbrt- UnxCmplt- RxOF- MalfTLP- ECRC+ UnsupReq+ ACSViol-
                UESvrt: DLP+ SDES- TLP+ FCP+ CmpltTO- CmpltAbrt- UnxCmplt- RxOF+ MalfTLP+ ECRC- UnsupReq- ACSViol-
                CESta:  RxErr- BadTLP- BadDLLP- Rollover- Timeout- AdvNonFatalErr-
                CEMsk:  RxErr- BadTLP- BadDLLP- Rollover- Timeout- AdvNonFatalErr-
                AERCap: First Error Pointer: 08, ECRCGenCap+ ECRCGenEn- ECRCChkCap+ ECRCChkEn-
                        MultHdrRecCap- MultHdrRecEn- TLPPfxPres- HdrLogCap-
                HeaderLog: 00000000 00000000 00000000 00000000
        Capabilities: [150 v1] Alternative Routing-ID Interpretation (ARI)
                ARICap: MFVC- ACS-, Next Function: 0
                ARICtl: MFVC- ACS-, Function Group: 0
        Capabilities: [180 v1] Single Root I/O Virtualization (SR-IOV)
                IOVCap: Migration-, Interrupt Message Number: 000
                IOVCtl: Enable- Migration- Interrupt- MSE- ARIHierarchy+
                IOVSta: Migration-
                Initial VFs: 16, Total VFs: 16, Number of VFs: 0, Function Dependency Link: 00
                VF offset: 1, stride: 1, Device ID: 101e
                Supported Page Size: 000007ff, System Page Size: 00000001
                Region 0: Memory at 000005e046000000 (64-bit, prefetchable)
                VF Migration: offset: 00000000, BIR: 0
        Capabilities: [1c0 v1] Secondary PCI Express
                LnkCtl3: LnkEquIntrruptEn- PerformEqu-
                LaneErrStat: 0
        Capabilities: [320 v1] Lane Margining at the Receiver <?>
        Capabilities: [370 v1] Physical Layer 16.0 GT/s <?>
        Capabilities: [3b0 v1] Extended Capability ID 0x2a
        Capabilities: [420 v1] Data Link Feature <?>
        Kernel driver in use: mlx5_core
        Kernel modules: mlx5_core
=
```