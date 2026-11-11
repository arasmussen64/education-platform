# Wrong: the files are right, but the two spinners on CPU 0 are left
# running after the walkthrough.
nohup taskset -c 0 spin > /dev/null 2>&1 &
nohup taskset -c 0 spin > /dev/null 2>&1 &
sudo systemctl set-property --runtime shop-cache MemoryHigh=64M
sleep 10
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt
sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity
printf 'web-1 1\narm-1 2\ndb-1 48\n' > ~/example/cores.txt
echo '0 48' > ~/example/siblings.txt
