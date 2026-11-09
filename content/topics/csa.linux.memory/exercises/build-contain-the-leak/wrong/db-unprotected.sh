# Wrong: the leak is contained, but the database is as likely a victim as
# anything else the next time memory runs out.
sleep 3; mkdir -p ~/report && cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak > ~/report/peak.txt
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer
sleep 10
