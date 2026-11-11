# Wrong: the cache is squeezed and its count saved, but the throttle is
# never taken off again, so the cache stays slow.
sudo systemctl set-property --runtime shop-cache MemoryHigh=64M
sleep 10
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt
printf 'web-1 1\narm-1 2\ndb-1 48\n' > ~/example/cores.txt
echo '0 48' > ~/example/siblings.txt
