# Wrong: the run queue reads vmstat's second column (b, blocked) instead of
# the first (r, runnable). On a quiet laptop b is 0, but a container's vmstat
# reads the whole machine, so on a busy CI runner it was 1 or more and this
# passed once; the check now hands the script a vmstat whose b is 3.
cat > ~/bin/triage-report <<'INNER'
#!/bin/bash
echo "cpus: $(nproc)"
echo "load: $(cut -d' ' -f1 /proc/loadavg)"
echo "run-queue: $(vmstat 1 2 | tail -1 | awk '{print $2}')"
echo "busiest: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1}')"
echo "busiest-cpu: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $2}')"
INNER
chmod +x ~/bin/triage-report
