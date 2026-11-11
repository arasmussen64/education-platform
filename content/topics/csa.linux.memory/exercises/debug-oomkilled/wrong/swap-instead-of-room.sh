# Wrong: the indexer and the database are fixed, but the cache keeps its
# 32 MB limit and is allowed to swap instead. It stays up, with most of
# its 100 MB pushed out to disk, which is no way for a cache to run.
sudo mkdir -p /etc/systemd/system/shop-cache.service.d /etc/systemd/system/shop-indexer.service.d /etc/systemd/system/shop-db.service.d
printf '[Service]\nMemorySwapMax=infinity\n' | sudo tee /etc/systemd/system/shop-cache.service.d/override.conf > /dev/null
printf '[Service]\nMemoryMax=512M\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer shop-db || true
sleep 5
