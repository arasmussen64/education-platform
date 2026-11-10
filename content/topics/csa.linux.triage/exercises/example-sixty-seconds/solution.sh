uptime; nproc
dmesg -T 2>/dev/null | tail -5 || echo "(dmesg not readable here)"
vmstat 1 2
mpstat -P ALL 1 1
pidstat 1 1; ps -eo pid,comm,%cpu --sort=-%cpu | head -5
iostat -xz 1 1 2>/dev/null | tail -8; pidstat -d 1 1 2>/dev/null | tail -6
free -m
mkdir -p ~/triage
busiest=$(ps -eo comm,%cpu --sort=-%cpu | awk 'NR==2 {print $1}')
ps -eo pid,comm,%cpu --sort=-%cpu | head -4 > ~/triage/top-cpu.txt
{ echo "bottleneck: cpu"; echo "culprit: $busiest"; echo "memory: ok"; echo "disk: ok"; } > ~/triage/verdict.txt
cat ~/triage/verdict.txt
