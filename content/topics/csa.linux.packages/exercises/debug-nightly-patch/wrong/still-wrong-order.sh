# Wrong: the hold and the path are fixed, but upgrade still runs before
# update, so on a fresh night it still finds nothing.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt upgrade -y
sudo apt update
sudo apt-mark hold shop-report
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
