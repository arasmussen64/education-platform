# Wrong: the cache and the database are fixed, but the indexer's limit is
# still 512 bytes.
sudo mkdir -p /etc/systemd/system/shop-cache.service.d /etc/systemd/system/shop-db.service.d
printf '[Service]\nMemoryMax=256M\n' | sudo tee /etc/systemd/system/shop-cache.service.d/override.conf > /dev/null
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer shop-db || true
sleep 5
