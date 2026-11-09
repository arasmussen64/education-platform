# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/cpu-cap <<'EOF'
#!/bin/bash
# Usage: cpu-cap SERVICE PERCENT
# Caps a service at PERCENT of one CPU with a drop-in, and shows the result.
service="$1"
percent="$2"
dropin_dir="/etc/systemd/system/$service.service.d"
sudo mkdir -p "$dropin_dir"
printf '[Service]\nCPUQuota=%s%%\n' "$percent" | sudo tee "$dropin_dir/override.conf" > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart "$service"
cat "/sys/fs/cgroup/system.slice/$service.service/cpu.max"
EOF
chmod +x ~/bin/cpu-cap
~/bin/cpu-cap shop-worker 30
top -b -n 2 -d 1 | grep shop-worker | tail -n 1
~/bin/cpu-cap shop-worker 60
