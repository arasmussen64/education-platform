# Wrong: the weight went on the report instead of the API, so under
# contention the batch job wins.
sudo mkdir -p /etc/systemd/system/shop-report.service.d
printf '[Service]\nCPUQuota=25%%\nCPUWeight=300\n' | sudo tee /etc/systemd/system/shop-report.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-report
sleep 2
mkdir -p ~/report
cat /sys/fs/cgroup/system.slice/shop-report.service/cpu.max > ~/report/cpu.txt
cat /sys/fs/cgroup/system.slice/shop-report.service/cpu.weight >> ~/report/cpu.txt
