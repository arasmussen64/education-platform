# Wrong: every machine's CPUs halved, as if every vCPU were half a core.
# arm-1's two vCPUs are two whole cores, one thread each.
sudo systemctl set-property --runtime shop-cache MemoryHigh=64M
sleep 10
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt
sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity
printf 'web-1 1\narm-1 1\ndb-1 48\n' > ~/example/cores.txt
echo '0 48' > ~/example/siblings.txt
