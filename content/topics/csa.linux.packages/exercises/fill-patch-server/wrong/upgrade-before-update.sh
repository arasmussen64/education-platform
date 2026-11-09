# Wrong: upgrade runs before update, so apt works from an old (here, empty)
# list and finds nothing to upgrade.
cat > ~/bin/patch-server <<'EOF'
#!/bin/bash
set -e
sudo apt upgrade -y
sudo apt update
apt list --upgradable 2>/dev/null
sudo apt-mark hold shop-report
if [ -f /run/reboot-required ]; then
  echo "reboot needed: $(tr '\n' ' ' < /run/reboot-required.pkgs)"
else
  echo "no reboot needed"
fi
EOF
