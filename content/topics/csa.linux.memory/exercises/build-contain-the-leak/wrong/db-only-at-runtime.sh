# Wrong: the leak is contained, but the database is protected only on the
# running process, through /proc. Its unit says nothing, so the next
# restart puts it back to 0, as likely a victim as anything else.
peak=/sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak
for _ in $(seq 1 30); do [ "$(cat "$peak")" -gt 150000000 ] && break; sleep 1; done
mkdir -p ~/report && cat "$peak" > ~/report/peak.txt
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer
sleep 10
echo -900 | sudo tee "/proc/$(systemctl show shop-db -p MainPID --value)/oom_score_adj" > /dev/null
