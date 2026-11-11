# Wrong: everything is contained, but the peak was saved after the limit
# was on. The restart gave the service a new cgroup, whose memory.peak
# started again from nothing and can't pass 128 MB, so the report says
# nothing about how bad the leak was.
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer
sleep 12
mkdir -p ~/report && cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak > ~/report/peak.txt
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
