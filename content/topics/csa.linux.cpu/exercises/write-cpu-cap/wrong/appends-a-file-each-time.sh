# Wrong: a new drop-in file per run, so the caps pile up and the last one
# written wins by alphabetical accident.
mkdir -p ~/bin
cat > ~/bin/cpu-cap <<'EOF'
#!/bin/bash
service="$1"
percent="$2"
dropin_dir="/etc/systemd/system/$service.service.d"
sudo mkdir -p "$dropin_dir"
printf '[Service]\nCPUQuota=%s%%\n' "$percent" | sudo tee "$dropin_dir/cap-$percent.conf" > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart "$service"
cat "/sys/fs/cgroup/system.slice/$service.service/cpu.max"
EOF
chmod +x ~/bin/cpu-cap
