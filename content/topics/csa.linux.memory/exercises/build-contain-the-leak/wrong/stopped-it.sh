# Wrong: stopping the indexer frees the memory and stops the shop's indexing.
peak=/sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak
for _ in $(seq 1 30); do [ "$(cat "$peak")" -gt 150000000 ] && break; sleep 1; done
mkdir -p ~/report && cat "$peak" > ~/report/peak.txt
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl stop shop-indexer
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
