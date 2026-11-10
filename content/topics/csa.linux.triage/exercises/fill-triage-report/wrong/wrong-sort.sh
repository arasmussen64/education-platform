# Wrong: the sort key is ascending (%cpu), so the busiest line names an idle
# process instead of the worker.
cat > ~/bin/triage-report <<'INNER'
#!/bin/bash
echo "cpus: $(nproc)"
echo "load: $(cut -d' ' -f1 /proc/loadavg)"
echo "run-queue: $(vmstat 1 2 | tail -1 | awk '{print $1}')"
echo "busiest: $(ps -eo comm,%cpu --sort=%cpu | awk 'NR == 2 {print $1}')"
echo "busiest-cpu: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $2}')"
INNER
chmod +x ~/bin/triage-report
