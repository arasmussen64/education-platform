# Wrong: the hold is taken out of the script, and shop-report is kept at 2.0
# by a pin file made by hand at the prompt instead. Tonight that works, but
# the script itself keeps nothing back, so on a server without that file (a
# new one) it installs the untested 2.1.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt upgrade -y
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
printf 'Package: shop-report\nPin: version 2.0\nPin-Priority: 1001\n' | sudo tee /etc/apt/preferences.d/shop-report > /dev/null
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
