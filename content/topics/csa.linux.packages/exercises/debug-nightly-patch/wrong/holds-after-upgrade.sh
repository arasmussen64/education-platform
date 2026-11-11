# Wrong: update now comes before upgrade and the right package is named,
# but the hold still comes after the upgrade, where the script had it. By
# the time shop-report is held, the untested 2.1 is already installed.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt upgrade -y
sudo apt-mark hold shop-report
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
