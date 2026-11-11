# Wrong: every machine's CPU count written as its cores, as if each vCPU
# were a core of its own. web-1 and db-1 have two threads on every core.
sudo systemctl set-property --runtime shop-cache MemoryHigh=64M
sleep 10
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt
sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity
printf 'web-1 2\narm-1 2\ndb-1 96\n' > ~/example/cores.txt
echo '0 48' > ~/example/siblings.txt
