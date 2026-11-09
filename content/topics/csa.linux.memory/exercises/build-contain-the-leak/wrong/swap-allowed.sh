# Wrong: with swap allowed, a leaking service can push its pages to disk
# instead of being stopped, and take the whole machine with it slowly.
sleep 3; mkdir -p ~/report && cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak > ~/report/peak.txt
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer
sleep 10
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
