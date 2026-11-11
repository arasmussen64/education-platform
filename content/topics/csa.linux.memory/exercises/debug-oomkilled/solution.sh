# The three faults:
#   1. shop-cache had MemoryMax=32M, but its working set is about 100 MB,
#      so the kernel killed it every time it warmed up. (memory.peak sat at
#      the limit before each kill; once the limit has room, it reads about
#      110 MB.) 256M gives it that room and is still a limit.
#   2. shop-indexer had MemoryMax=512: 512 *bytes*. A limit needs a unit:
#      512M. Not even the interpreter could start.
#   3. shop-db had OOMScoreAdjust=1000, which makes it the kernel's FIRST
#      choice of victim. A database should be the last: -900.
# Drop-ins fix a unit without editing it; in the lab you'd write them with
# sudo systemctl edit NAME. The units' MemorySwapMax=0 is left alone.
sudo mkdir -p /etc/systemd/system/shop-cache.service.d /etc/systemd/system/shop-indexer.service.d /etc/systemd/system/shop-db.service.d
printf '[Service]\nMemoryMax=256M\n' | sudo tee /etc/systemd/system/shop-cache.service.d/override.conf > /dev/null
printf '[Service]\nMemoryMax=512M\n' | sudo tee /etc/systemd/system/shop-indexer.service.d/override.conf > /dev/null
printf '[Service]\nOOMScoreAdjust=-900\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-cache shop-indexer shop-db
sleep 5
systemctl is-active shop-cache shop-indexer shop-db
cat /sys/fs/cgroup/system.slice/shop-cache.service/memory.peak /sys/fs/cgroup/system.slice/shop-indexer.service/memory.peak
cat /proc/$(systemctl show shop-db -p MainPID --value)/oom_score_adj
