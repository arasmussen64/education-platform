# Wrong: throttled_usec is how long the group spent throttled, in
# microseconds, not how many periods it was throttled in.
cat > ~/bin/cpu-report <<'EOF'
#!/bin/bash
service="$1"
echo "cpus: $(nproc)"
echo "load: $(awk '{print $1, $2, $3}' /proc/loadavg)"
echo "top process: $(ps -eo comm,%cpu --sort=-%cpu | awk 'NR == 2 {print $1, $2 "%"}')"
echo "throttled periods of $service: $(awk '/^throttled_usec/ {print $2}' /sys/fs/cgroup/system.slice/$service.service/cpu.stat)"
EOF
