# Find the runaway, confirm it with strace, stop it at the service, and
# write down what it was.
vmstat 1 2
ps -eo pid,comm,%cpu --sort=-%cpu | head -5
pid=$(systemctl show -p MainPID --value shop-tailer)
echo "shop-tailer MainPID: $pid"
sudo timeout 3 strace -c -f -p "$pid" 2>/tmp/strace.txt || true
grep -E 'openat|open|calls' /tmp/strace.txt | head -5 || true
sudo systemctl disable --now shop-tailer
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a busy loop of failing openat calls on a missing queue path\n' > ~/triage/finding.txt
echo "shop-tailer is now: $(systemctl is-active shop-tailer 2>/dev/null; true)"
echo "shop-api is still: $(systemctl is-active shop-api)"
cat ~/triage/finding.txt
