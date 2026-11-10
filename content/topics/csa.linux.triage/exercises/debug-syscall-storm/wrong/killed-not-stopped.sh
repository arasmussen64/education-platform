# Wrong: killed the process instead of stopping the service. The unit has
# Restart=always, so systemd brings it straight back and the CPU is eaten
# again.
pid=$(systemctl show -p MainPID --value shop-tailer)
sudo kill -9 "$pid" 2>/dev/null || true
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a busy loop of failing openat calls on a missing queue path\n' > ~/triage/finding.txt
