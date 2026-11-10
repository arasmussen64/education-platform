# 1. What's busy, and how busy the machine is.
top -b -n 1 | head -n 12
uptime; nproc
ps -eo comm,%cpu --sort=-%cpu | head -n 4

# 2. The report is a batch job: a quarter of a CPU, as a drop-in. (In the lab
#    you'd write it with sudo systemctl edit shop-report.)
sudo mkdir -p /etc/systemd/system/shop-report.service.d
printf '[Service]\nCPUQuota=25%%\n' | sudo tee /etc/systemd/system/shop-report.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-report
sleep 2
cat /sys/fs/cgroup/system.slice/shop-report.service/cpu.max
grep -E '^(nr_throttled|throttled_usec)' /sys/fs/cgroup/system.slice/shop-report.service/cpu.stat

# 3. The API wins under contention: three times the default weight, no quota.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUWeight=300\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
cat /sys/fs/cgroup/system.slice/shop-api.service/cpu.weight

# 4. The report file.
mkdir -p ~/report
cat /sys/fs/cgroup/system.slice/shop-report.service/cpu.max > ~/report/cpu.txt
cat /sys/fs/cgroup/system.slice/shop-api.service/cpu.weight >> ~/report/cpu.txt
cat ~/report/cpu.txt
