# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/cpu-report <<'EOF'
#!/bin/bash
# Usage: cpu-report SERVICE
# How the CPUs are doing, and whether SERVICE is being throttled.
service="$1"
echo "cpus: $(nproc)"
echo "load: $(awk '{print $1, $2, $3}' /proc/loadavg)"
echo "top process: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1, $2 "%"}')"
echo "throttled periods of $service: $(awk '/^nr_throttled/ {print $2}' /sys/fs/cgroup/system.slice/$service.service/cpu.stat)"
EOF
~/bin/cpu-report shop-worker
