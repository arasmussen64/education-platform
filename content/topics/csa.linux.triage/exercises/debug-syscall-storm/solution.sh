# From the whole machine down to one process: the split of CPU time, then
# who is using it, then which service that process belongs to.
vmstat 1 2
pidstat 1 2 | tail -n 4
ps -eo pid,comm,%cpu --sort=-%cpu | head -n 5
pid=$(systemctl show -p MainPID --value shop-tailer)
systemctl status "$pid" --no-pager | head -n 4

# What is it asking the kernel for? Count its system calls for three
# seconds. One call, openat, fails every single time: the program is
# opening a file that isn't there, in a loop with no pause.
sudo timeout 3 strace -c -f -p "$pid" 2>/tmp/strace.txt || true
head -n 8 /tmp/strace.txt

# Stop it at the service: the unit has Restart=always, so a killed process
# is back within a second, but a unit stopped through systemd stays
# stopped. "disable" also takes it out of the next boot; "--now" stops it.
sudo systemctl disable --now shop-tailer

# The note for the next person.
mkdir -p ~/triage
printf 'culprit: shop-tailer\ncause: a busy loop of failing openat calls on a missing queue path\n' > ~/triage/finding.txt
echo "shop-tailer is now: $(systemctl is-active shop-tailer 2>/dev/null; true), $(systemctl is-enabled shop-tailer 2>/dev/null; true)"
echo "shop-api is still: $(systemctl is-active shop-api)"
cat ~/triage/finding.txt
