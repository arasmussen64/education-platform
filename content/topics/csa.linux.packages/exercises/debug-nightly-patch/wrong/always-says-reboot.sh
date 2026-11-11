# Wrong: the order and the hold are fixed, but instead of looking for the
# reboot note the script always prints "reboot needed". Right on a night
# with a new kernel, wrong on every other night.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt-mark hold shop-report
sudo apt upgrade -y
echo "reboot needed"
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
