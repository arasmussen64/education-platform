# Wrong: the run queue reads vmstat's second column (b, blocked, which is 0)
# instead of the first (r, runnable).
cat > ~/bin/triage-report <<'INNER'
#!/bin/bash
echo "cpus: $(nproc)"
echo "load: $(cut -d' ' -f1 /proc/loadavg)"
echo "run-queue: $(vmstat 1 2 | tail -1 | awk '{print $2}')"
echo "busiest: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1}')"
echo "busiest-cpu: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $2}')"
INNER
chmod +x ~/bin/triage-report
