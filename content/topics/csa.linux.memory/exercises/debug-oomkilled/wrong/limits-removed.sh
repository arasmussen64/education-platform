# Wrong: nothing is killed any more because both limits are gone
# (MemoryMax=infinity). The cache and the indexer stay up, and nothing
# protects the rest of the machine from the next leak.
sudo mkdir -p /etc/systemd/system/shop-cache.service.d /etc/systemd/system/shop-indexer.service.d /etc/systemd/system/shop-db.service.d
printf '[Service]\nMemoryMax=infinity\n' | sudo tee /etc/systemd/system/shop-cache.service.d/override.conf > /dev/null
printf '[Service]\nMemoryMax=infinity\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer shop-db || true
sleep 5
