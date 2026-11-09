# Wrong: the cap went on the API, which now answers slowly on an idle
# machine, and the report runs free.
sudo mkdir -p /etc/systemd/system/shop-report.service.d /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=25%%\nCPUWeight=300\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-api shop-report
sleep 2
mkdir -p ~/report
cat /sys/fs/cgroup/system.slice/shop-report.service/cpu.max > ~/report/cpu.txt
cat /sys/fs/cgroup/system.slice/shop-api.service/cpu.weight >> ~/report/cpu.txt
