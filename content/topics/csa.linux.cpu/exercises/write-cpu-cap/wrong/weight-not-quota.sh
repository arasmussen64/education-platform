# Wrong: CPUWeight is a share under contention, not a cap; on an idle
# machine the worker still takes a whole CPU.
mkdir -p ~/bin
cat > ~/bin/cpu-cap <<'EOF'
#!/bin/bash
service="$1"
percent="$2"
dropin_dir="/etc/systemd/system/$service.service.d"
sudo mkdir -p "$dropin_dir"
printf '[Service]\nCPUWeight=%s\n' "$percent" | sudo tee "$dropin_dir/override.conf" > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart "$service"
cat "/sys/fs/cgroup/system.slice/$service.service/cpu.max"
EOF
chmod +x ~/bin/cpu-cap
