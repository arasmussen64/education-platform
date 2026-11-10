# The finished report. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/triage-report <<'EOF'
#!/bin/bash
# Usage: triage-report
# The first-minute signals in one place: the CPU count, the load, the run
# queue, and the busiest process with its CPU share.
echo "cpus: $(nproc)"
echo "load: $(cut -d' ' -f1 /proc/loadavg)"
echo "run-queue: $(vmstat 1 2 | tail -1 | awk '{print $1}')"
echo "busiest: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1}')"
echo "busiest-cpu: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $2}')"
EOF
chmod +x ~/bin/triage-report
~/bin/triage-report
