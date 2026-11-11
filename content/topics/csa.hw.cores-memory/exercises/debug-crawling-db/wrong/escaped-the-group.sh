# Wrong: the CPU cap is raised properly, and then the database's process is
# moved out of its control group into one of its own making, out of reach of
# the memory throttle and the CPU list. systemd still has MemoryHigh=48M and
# AllowedCPUs=0 for shop-db, and the next restart puts the process back
# under them.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 2
sudo mkdir -p /sys/fs/cgroup/system.slice/escape
systemctl show shop-db -p MainPID --value | sudo tee /sys/fs/cgroup/system.slice/escape/cgroup.procs > /dev/null
sleep 3
