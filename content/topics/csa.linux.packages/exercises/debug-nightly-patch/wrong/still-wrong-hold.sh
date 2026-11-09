# Wrong: the order and the path are fixed, but the agent is still the one
# held, so its security fix is skipped and the untested report goes in.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt-mark hold shop-agent
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
~/bin/nightly-patch
