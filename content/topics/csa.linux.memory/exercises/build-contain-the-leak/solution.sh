# 1. Who's eating the memory, and how much has its service used? Read the
#    peak before changing anything: once the limit is on, the service is
#    killed and restarted, and each restart starts the count again.
free -m; sleep 3; free -m
ps -eo pid,comm,rss --sort=-rss | head -n 4
# The PID at the top of that list; systemctl status PID names its service.
pid=$(ps -eo pid --sort=-rss | sed -n 2p | tr -d ' ')
systemctl status "$pid" --no-pager | head -n 12
cat /sys/fs/cgroup/system.slice/shop-indexer.service/memory.current
# A person reading this has watched for a while, and the peak is hundreds
# of MB. This script runs seconds after boot, so it waits until the leak has
# passed 128 MB: no run under the limit can reach a peak like that.
peak=/sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak
for _ in $(seq 1 30); do [ "$(cat "$peak")" -gt 150000000 ] && break; sleep 1; done
mkdir -p ~/report && cat "$peak" | tee ~/report/peak.txt

# 2. A hard limit and no swap, as a drop-in. (In the lab you'd write it with
#    sudo systemctl edit shop-indexer; here the file is written directly.)
sudo mkdir -p /etc/systemd/system/shop-indexer.service.d
printf '[Service]\nMemoryMax=128M\nMemorySwapMax=0\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-indexer

# 3. Watch the kernel kill it at the limit and systemd bring it back. The
#    leak takes about eight seconds to reach 128 MB.
sleep 12
journalctl -u shop-indexer --no-pager | grep -i oom | tail -n 3
systemctl show shop-indexer -p NRestarts
journalctl -k --no-pager | grep 'Killed process' | tail -n 1

# 4. The database is never the victim.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
cat /proc/$(systemctl show shop-db -p MainPID --value)/oom_score_adj
