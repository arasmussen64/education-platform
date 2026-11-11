# Wrong: shop-report is held by hand at the prompt, and the hold line is
# taken out of the script. Tonight that works, but the script itself keeps
# nothing back, so on a server where the hold isn't set (a new one, or after
# someone releases it) it installs the untested 2.1.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
sudo apt-mark hold shop-report
~/bin/nightly-patch
