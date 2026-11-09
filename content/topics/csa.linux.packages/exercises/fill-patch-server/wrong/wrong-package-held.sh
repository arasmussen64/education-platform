# Wrong: the agent is held instead of the report tool, so the security fix
# is skipped and the untested report goes in.
cat > ~/bin/patch-server <<'EOF'
#!/bin/bash
set -e
sudo apt update
apt list --upgradable 2>/dev/null
sudo apt-mark hold shop-agent
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed: $(tr '\n' ' ' < /run/reboot-required.pkgs)"
else
  echo "no reboot needed"
fi
EOF
