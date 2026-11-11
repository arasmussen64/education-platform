# Wrong: both limits are fixed in drop-ins, but the database is protected
# only on the running process, through /proc. Its unit still says 1000, so
# the next restart makes it the kernel's first choice of victim again.
sudo mkdir -p /etc/systemd/system/shop-cache.service.d /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=256M\n' | sudo tee /etc/systemd/system/shop-cache.service.d/override.conf > /dev/null
printf '[Service]\nMemoryMax=512M\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer || true
echo -900 | sudo tee "/proc/$(systemctl show shop-db -p MainPID --value)/oom_score_adj" > /dev/null
sleep 5
