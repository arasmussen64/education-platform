free -m
grep -E '^(MemTotal|MemFree|MemAvailable|Cached):' /proc/meminfo
vmstat 1 3
sudo systemd-run --unit=hog -p MemoryMax=64M -p MemorySwapMax=0 memhog 200
sleep 3; systemctl show hog -p Result,ExecMainStatus
journalctl -k --no-pager | grep 'Killed process' | tail -n 1
mkdir -p ~/example && systemctl show hog -p Result --value > ~/example/result.txt && grep '^MemAvailable:' /proc/meminfo > ~/example/available.txt
