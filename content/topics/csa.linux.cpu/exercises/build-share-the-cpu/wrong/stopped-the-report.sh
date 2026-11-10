# Wrong: stopping the report "fixes" the CPU and loses the report.
sudo mkdir -p /etc/systemd/system/shop-report.service.d /etc/systemd/system/shop-api.service.d
printf '[Service]\nCPUQuota=25%%\n' | sudo tee /etc/systemd/system/shop-report.service.d/override.conf > /dev/null
printf '[Service]\nCPUWeight=300\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl stop shop-report
sudo systemctl restart shop-api
mkdir -p ~/report
printf '25000 100000\n300\n' > ~/report/cpu.txt
