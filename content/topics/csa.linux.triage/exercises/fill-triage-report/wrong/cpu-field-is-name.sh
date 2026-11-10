# Wrong: the busiest-cpu line reads field 1 (the process name) instead of
# field 2 (its CPU percentage), so it prints a name where a number belongs.
cat > ~/bin/triage-report <<'INNER'
#!/bin/bash
echo "cpus: $(nproc)"
echo "load: $(cut -d' ' -f1 /proc/loadavg)"
echo "run-queue: $(vmstat 1 2 | tail -1 | awk '{print $1}')"
echo "busiest: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1}')"
echo "busiest-cpu: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1}')"
INNER
chmod +x ~/bin/triage-report
