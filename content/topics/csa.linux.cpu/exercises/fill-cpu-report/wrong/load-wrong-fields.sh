# Wrong: the fourth field of /proc/loadavg is running/total tasks, not a load average.
cat > ~/bin/cpu-report <<'EOF'
#!/bin/bash
service="$1"
echo "cpus: $(nproc)"
echo "load: $(awk '{print $1, $2, $4}' /proc/loadavg)"
echo "top process: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1, $2 "%"}')"
echo "throttled periods of $service: $(awk '/^nr_throttled/ {print $2}' /sys/fs/cgroup/system.slice/$service.service/cpu.stat)"
EOF
