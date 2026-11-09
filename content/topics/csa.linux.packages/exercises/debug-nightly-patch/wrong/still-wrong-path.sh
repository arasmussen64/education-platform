# Wrong: the order and the hold are fixed, but the script still looks for
# the reboot note in /etc, so it never says one is needed.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
if [ -f /etc/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
