lscpu | grep -E '^(CPU\(s\)|Thread|Core|Socket|NUMA node\(s\)|Hypervisor)'
lscpu --sysroot /srv/machines/web-1 | grep -E '^(CPU\(s\)|Thread|Core|Socket)'
lscpu --sysroot /srv/machines/arm-1 | grep -E '^(Architecture|CPU\(s\)|Vendor|Model name|Thread|Core|Socket)'
lscpu --sysroot /srv/machines/db-1 | grep -E '^(CPU\(s\)|Thread|Core|Socket|NUMA)'; lscpu --sysroot /srv/machines/db-1 -e=CPU,NODE,SOCKET,CORE | awk 'NR == 1 || $4 == 0'
lscpu --sysroot /srv/machines/db-1 -p=CORE,SOCKET | grep -v '^#' | sort -u | wc -l
cat /srv/machines/db-1/numactl-hardware.txt; numactl --hardware
taskset -c 0 spin & taskset -c 0 spin & sleep 3; ps -o pid,psr,pcpu,comm -C spin; kill %1 %2
head -n 1 /proc/stat; sleep 5; head -n 1 /proc/stat
journalctl -u shop-cache -n 3 -o cat; sudo systemctl set-property --runtime shop-cache MemoryHigh=64M; sleep 20; journalctl -u shop-cache -n 3 -o cat
grep -E '^(high|max|oom_kill) ' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events; cat /sys/fs/cgroup/system.slice/shop-cache.service/memory.current; systemctl is-active shop-cache
mkdir -p ~/example && awk '$1 == "high" {print $2}' /sys/fs/cgroup/system.slice/shop-cache.service/memory.events > ~/example/squeeze.txt; cat ~/example/squeeze.txt
sudo systemctl set-property --runtime shop-cache MemoryHigh=infinity; sleep 5; journalctl -u shop-cache -n 2 -o cat
sudo systemctl set-property --runtime shop-cache AllowedCPUs=0; taskset -cp "$(systemctl show shop-cache -p MainPID --value)"
sudo systemctl set-property --runtime shop-cache AllowedCPUs=; taskset -cp "$(systemctl show shop-cache -p MainPID --value)"; sudo systemctl restart shop-cache; taskset -cp "$(systemctl show shop-cache -p MainPID --value)"
printf 'web-1 1\narm-1 2\ndb-1 48\n' > ~/example/cores.txt; echo '0 48' > ~/example/siblings.txt; cat ~/example/cores.txt ~/example/siblings.txt
