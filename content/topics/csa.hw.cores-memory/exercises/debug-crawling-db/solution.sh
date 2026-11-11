# The three faults, in shop-db's unit and its drop-in 10-tuning.conf:
#   1. CPUQuota=10%: a tenth of a CPU for a database whose work keeps one
#      CPU busy. nr_throttled in its cpu.stat climbs every period. The cap
#      stays, raised to the allowance: one and a half CPUs, which is more
#      than the one its work needs (a cap of exactly one still throttles).
#   2. MemoryHigh=48M, a throttle far below the 150 MB it keeps its tables
#      in: memory.events counts "high" climbing, memory.current sits at the
#      throttle, swap fills, and the service is alive and crawling. The
#      throttle goes; the 256 MB wall (MemoryMax) and swap stay.
#   3. AllowedCPUs=0: pinned to CPU 0, the batch job's CPU, so the two take
#      turns on it while the other CPUs idle (taskset -cp shows it). An
#      empty AllowedCPUs= frees it, and the restart starts the process
#      afresh: a running process keeps the CPUs it was given.
# One drop-in overrides all three, because a drop-in read later wins; in the
# lab you'd write it with sudo systemctl edit shop-db, which names it
# override.conf and reloads systemd for you.
sudo mkdir -p /etc/systemd/system/shop-db.service.d
printf '[Service]\nCPUQuota=150%%\nMemoryHigh=infinity\nAllowedCPUs=\n' | sudo tee /etc/systemd/system/shop-db.service.d/override.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-db
sleep 3
systemctl show shop-db -p CPUQuotaPerSecUSec -p MemoryHigh -p MemoryMax -p AllowedCPUs
taskset -cp "$(systemctl show shop-db -p MainPID --value)"
journalctl -u shop-db -n 3 -o cat
