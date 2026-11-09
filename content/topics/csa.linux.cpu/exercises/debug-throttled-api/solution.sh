# The three mistakes, all in shop-api's unit:
#   1. CPUQuota=5%: a twentieth of a CPU for a service that has to answer
#      quickly. It used its 5 ms up at the start of every 100 ms period and
#      waited out the rest (nr_throttled climbed once per period). An API
#      shouldn't have a quota at all; the request/weight is what protects
#      others from it.
#   2. Nice=19: the lowest priority, so under any contention it ran last.
#   3. CPUWeight=1: the smallest possible share when CPUs are contended;
#      100 is the default.
# A drop-in overrides all three; in the lab you'd write it with
# sudo systemctl edit shop-api. An empty CPUQuota= clears the quota.
sudo mkdir -p /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=\nNice=0\nCPUWeight=100\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api
sleep 2
systemctl show shop-api -p CPUQuotaPerSecUSec,Nice,CPUWeight
ps -o pid,ni,comm -p "$(systemctl show shop-api -p MainPID --value)"
grep nr_throttled /sys/fs/cgroup/system.slice/shop-api.service/cpu.stat; sleep 2; grep nr_throttled /sys/fs/cgroup/system.slice/shop-api.service/cpu.stat
