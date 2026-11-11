# Wrong: the indexer and the database are fixed, but instead of giving the
# cache a limit it fits in, its program was edited to hold 20 MB instead of
# 100 MB. It stays up inside the 32 MB limit, and it is no longer much of a
# cache.
sudo sed -i 's/100 \* 1024 \* 1024/20 * 1024 * 1024/' /usr/local/bin/shop-cache
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d /etc/systemd/system/shop-db.service.d
printf '[Service]\nMemoryMax=512M\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer shop-db || true
sleep 5
