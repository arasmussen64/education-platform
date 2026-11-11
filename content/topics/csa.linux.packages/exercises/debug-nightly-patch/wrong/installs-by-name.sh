# Wrong: instead of upgrading everything but shop-report, the script
# installs last night's two security fixes by name. That's right tonight,
# but an update for any other package is never installed.
cat > ~/bin/nightly-patch <<'EOF'
#!/bin/bash
set -e
sudo apt update
sudo apt install -y shop-agent linux-image-shop
if [ -f /run/reboot-required ]; then
  echo "reboot needed"
fi
EOF
sudo apt-mark unhold shop-agent
~/bin/nightly-patch
