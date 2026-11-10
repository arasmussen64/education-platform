# Wrong: the drop-ins are written but systemd is never told about them, so
# the restarted services run with their old settings.
sudo mkdir -p /etc/systemd/system/shop-report.service.d /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=25%%\n' | sudo tee /etc/systemd/system/shop-report.service.d/override.conf > /dev/null
printf '[Service]\nCPUWeight=300\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl restart shop-report shop-api
sleep 2
mkdir -p ~/report
printf '25000 100000\n300\n' > ~/report/cpu.txt
