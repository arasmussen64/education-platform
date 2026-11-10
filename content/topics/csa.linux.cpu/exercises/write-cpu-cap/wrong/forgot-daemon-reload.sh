# Wrong: the drop-in is written but systemd is never told, so the restart
# runs the service with the old settings.
mkdir -p ~/bin
cat > ~/bin/cpu-cap <<'EOF'
#!/bin/bash
service="$1"
percent="$2"
dropin_dir="/etc/systemd/system/$service.service.d"
sudo mkdir -p "$dropin_dir"
printf '[Service]\nCPUQuota=%s%%\n' "$percent" | sudo tee "$dropin_dir/override.conf" > /dev/null
sudo systemctl restart "$service"
cat "/sys/fs/cgroup/system.slice/$service.service/cpu.max"
EOF
chmod +x ~/bin/cpu-cap
