# 1. Who's eating the memory, and how much has its service used? Read the
#    peak before changing anything: once the limit is on, the service is
#    killed and restarted, and each restart starts the count again.
free -m; sleep 3; free -m
ps -eo pid,comm,rss --sort=-rss | head -n 4
systemctl status shop-indexer --no-pager | head -n 12
cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.current
mkdir -p ~/report && cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak | tee ~/report/peak.txt

# 2. A hard limit and no swap, as a drop-in. (In the lab you'd write it with
#    sudo systemctl edit shop-indexer; here the file is written directly.)
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer

# 3. Watch the kernel kill it at the limit and systemd bring it back.
sleep 10
journalctl -u shop-indexer --no-pager | grep -i oom | tail -n 3
systemctl show shop-indexer -p NRestarts
journalctl -k --no-pager | grep 'Killed process' | tail -n 1

# 4. The database is never the victim.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
cat /proc/$(systemctl show shop-db -p MainPID --value)/oom_score_adj
