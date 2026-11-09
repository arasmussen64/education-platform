nproc; uptime
spin & pid=$!; sleep 2; top -b -n 1 | head -n 12; kill $pid
sudo systemd-run --unit=spin -p CPUQuota=20% spin
sleep 3; cat /sys/fs/cgroup/system.slice/spin.service/cpu.max
top -b -n 1 | grep spin
grep -E '^(nr_periods|nr_throttled|throttled_usec)' /sys/fs/cgroup/system.slice/spin.service/cpu.stat
mkdir -p ~/example && grep throttled /sys/fs/cgroup/system.slice/spin.service/cpu.stat > ~/example/throttled.txt && sudo systemctl stop spin
