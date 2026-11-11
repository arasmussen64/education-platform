# The three faults, all in shop-api's unit:
#   1. CPUQuota=5%: a twentieth of a CPU for a service with a whole CPU's
#      worth of work. It used its 5 ms up at the start of every 100 ms
#      period and waited out the rest (nr_throttled climbed once per
#      period). The cap has to stay on this shared machine, so it is raised
#      to the two CPUs the machine's rule allows: the work needs one, and a
#      quota of exactly one still throttles now and then.
#   2. Nice=19: the lowest priority, so under any contention it ran last.
#   3. CPUWeight=1: the smallest possible share when CPUs are contended;
#      100 is the default.
# A drop-in overrides all three; in the lab you'd write it with
# sudo systemctl edit shop-api.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=200%%\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
systemctl show shop-api -p CPUQuotaPerSecUSec,Nice,CPUWeight
cat /sys/fs/cgroup/system.slice/shop-api.service/cpu.max
ps -o pid,ni,comm -p "$(systemctl show shop-api -p MainPID --value)"
grep nr_throttled /sys/fs/cgroup/system.slice/shop-api.service/cpu.stat; sleep 2; grep nr_throttled /sys/fs/cgroup/system.slice/shop-api.service/cpu.stat
