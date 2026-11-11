# Wrong: the CPU list is emptied again but the cache isn't restarted. systemd
# forgets the setting, and the running process stays on CPU 0.
sudo systemctl set-property --runtime shop-cache MemoryHigh=64M
sleep 10
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt
sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity
sudo systemctl set-property --runtime shop-cache AllowedCPUs=0
sudo systemctl set-property --runtime shop-cache AllowedCPUs=
printf 'web-1 1\narm-1 2\ndb-1 48\n' > ~/example/cores.txt
echo '0 48' > ~/example/siblings.txt
